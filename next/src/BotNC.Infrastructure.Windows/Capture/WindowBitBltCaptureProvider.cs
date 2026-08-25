using System.ComponentModel;
using System.Runtime.InteropServices;
using BotNC.Core.Capture;
using BotNC.Core.Windows;

namespace BotNC.Infrastructure.Windows.Capture;

public sealed class WindowBitBltCaptureProvider : IWindowCaptureProvider
{
    private const uint Srccopy = 0x00CC0020;
    private const uint CaptureBlt = 0x40000000;
    private const uint DibRgbColors = 0;
    private const int BiRgb = 0;

    public string Name => "BitBlt · janela selecionada";

    public ValueTask<CapturedFrame> CaptureWindowAsync(
        GameWindowTarget target,
        CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        if (!NativeMethods.IsWindow(target.Handle))
        {
            throw new InvalidOperationException(
                $"A janela {target.Title} não existe mais. Atualize a lista de clientes.");
        }

        if (!NativeMethods.GetClientRect(target.Handle, out var clientRect))
        {
            throw CreateWin32Exception("Não foi possível medir a área do cliente.");
        }

        var width = clientRect.Right - clientRect.Left;
        var height = clientRect.Bottom - clientRect.Top;
        if (width <= 0 || height <= 0)
        {
            throw new InvalidOperationException(
                $"A janela {target.Title} não possui uma área capturável.");
        }

        var windowDc = NativeMethods.GetDC(target.Handle);
        if (windowDc == IntPtr.Zero)
        {
            throw CreateWin32Exception("Não foi possível obter a superfície da janela.");
        }

        IntPtr memoryDc = IntPtr.Zero;
        IntPtr bitmap = IntPtr.Zero;
        IntPtr previousObject = IntPtr.Zero;

        try
        {
            memoryDc = NativeMethods.CreateCompatibleDC(windowDc);
            if (memoryDc == IntPtr.Zero)
            {
                throw CreateWin32Exception("Não foi possível criar a superfície de captura.");
            }

            var info = BitmapInfo.Create(width, height);
            bitmap = NativeMethods.CreateDIBSection(
                windowDc,
                ref info,
                DibRgbColors,
                out var pixelPointer,
                IntPtr.Zero,
                0);
            if (bitmap == IntPtr.Zero || pixelPointer == IntPtr.Zero)
            {
                throw CreateWin32Exception("Não foi possível criar o bitmap da janela.");
            }

            previousObject = NativeMethods.SelectObject(memoryDc, bitmap);
            if (previousObject == IntPtr.Zero || previousObject == new IntPtr(-1))
            {
                throw CreateWin32Exception("Não foi possível selecionar o bitmap da janela.");
            }

            cancellationToken.ThrowIfCancellationRequested();
            if (!NativeMethods.BitBlt(
                    memoryDc,
                    0,
                    0,
                    width,
                    height,
                    windowDc,
                    0,
                    0,
                    Srccopy | CaptureBlt))
            {
                throw CreateWin32Exception("O BitBlt não conseguiu capturar a janela.");
            }

            var stride = checked(width * 4);
            var pixels = new byte[checked(stride * height)];
            Marshal.Copy(pixelPointer, pixels, 0, pixels.Length);
            return ValueTask.FromResult(
                new CapturedFrame(width, height, stride, pixels, DateTimeOffset.Now));
        }
        finally
        {
            if (previousObject != IntPtr.Zero && previousObject != new IntPtr(-1))
            {
                NativeMethods.SelectObject(memoryDc, previousObject);
            }

            if (bitmap != IntPtr.Zero)
            {
                NativeMethods.DeleteObject(bitmap);
            }

            if (memoryDc != IntPtr.Zero)
            {
                NativeMethods.DeleteDC(memoryDc);
            }

            NativeMethods.ReleaseDC(target.Handle, windowDc);
        }
    }

    private static Win32Exception CreateWin32Exception(string message) =>
        new(Marshal.GetLastWin32Error(), message);

    [StructLayout(LayoutKind.Sequential)]
    private struct NativeRect
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct BitmapInfoHeader
    {
        public uint Size;
        public int Width;
        public int Height;
        public ushort Planes;
        public ushort BitCount;
        public int Compression;
        public uint SizeImage;
        public int XPelsPerMeter;
        public int YPelsPerMeter;
        public uint ClrUsed;
        public uint ClrImportant;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct BitmapInfo
    {
        public BitmapInfoHeader Header;
        public uint Colors;

        public static BitmapInfo Create(int width, int height) =>
            new()
            {
                Header = new BitmapInfoHeader
                {
                    Size = (uint)Marshal.SizeOf<BitmapInfoHeader>(),
                    Width = width,
                    Height = -height,
                    Planes = 1,
                    BitCount = 32,
                    Compression = BiRgb,
                    SizeImage = checked((uint)(width * height * 4))
                }
            };
    }

    private static class NativeMethods
    {
        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool IsWindow(IntPtr windowHandle);

        [DllImport("user32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool GetClientRect(IntPtr windowHandle, out NativeRect rectangle);

        [DllImport("user32.dll")]
        public static extern IntPtr GetDC(IntPtr windowHandle);

        [DllImport("user32.dll")]
        public static extern int ReleaseDC(IntPtr windowHandle, IntPtr deviceContext);

        [DllImport("gdi32.dll", SetLastError = true)]
        public static extern IntPtr CreateCompatibleDC(IntPtr deviceContext);

        [DllImport("gdi32.dll", SetLastError = true)]
        public static extern IntPtr CreateDIBSection(
            IntPtr deviceContext,
            ref BitmapInfo bitmapInfo,
            uint usage,
            out IntPtr bits,
            IntPtr section,
            uint offset);

        [DllImport("gdi32.dll", SetLastError = true)]
        public static extern IntPtr SelectObject(IntPtr deviceContext, IntPtr graphicObject);

        [DllImport("gdi32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool DeleteObject(IntPtr graphicObject);

        [DllImport("gdi32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool DeleteDC(IntPtr deviceContext);

        [DllImport("gdi32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool BitBlt(
            IntPtr destination,
            int destinationX,
            int destinationY,
            int width,
            int height,
            IntPtr source,
            int sourceX,
            int sourceY,
            uint rasterOperation);
    }
}
