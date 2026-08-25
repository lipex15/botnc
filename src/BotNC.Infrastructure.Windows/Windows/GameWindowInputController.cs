using System.ComponentModel;
using System.Runtime.InteropServices;
using BotNC.Core.Input;
using BotNC.Core.Windows;

namespace BotNC.Infrastructure.Windows.Windows;

public sealed class GameWindowInputController(IInputController foregroundInput)
    : IWindowInputController
{
    private const uint WmKeyDown = 0x0100;
    private const uint WmKeyUp = 0x0101;
    private const uint WmMouseMove = 0x0200;
    private const uint WmLeftButtonDown = 0x0201;
    private const uint WmLeftButtonUp = 0x0202;
    private const nuint MkLeftButton = 0x0001;
    private const uint MapVkToVsc = 0;
    private const int SwRestore = 9;

    public async Task SendKeyAsync(
        GameWindowTarget target,
        ushort virtualKey,
        WindowInputMode mode,
        CancellationToken cancellationToken)
    {
        ValidateWindow(target);
        if (mode == WindowInputMode.BackgroundMessages)
        {
            await PostKeyAsync(target.Handle, virtualKey, cancellationToken);
            return;
        }

        await ActivateAsync(target, cancellationToken);
        await foregroundInput.PressKeyAsync(virtualKey, cancellationToken);
    }

    public async Task SendClickAsync(
        GameWindowTarget target,
        int clientX,
        int clientY,
        WindowInputMode mode,
        CancellationToken cancellationToken)
    {
        ValidateWindow(target);
        if (clientX < 0 || clientY < 0 || clientX > ushort.MaxValue || clientY > ushort.MaxValue)
        {
            throw new ArgumentOutOfRangeException(
                nameof(clientX),
                $"Coordenada cliente inválida: ({clientX}, {clientY}).");
        }

        if (mode == WindowInputMode.BackgroundMessages)
        {
            await PostClickAsync(target.Handle, clientX, clientY, cancellationToken);
            return;
        }

        await ActivateAsync(target, cancellationToken);
        var point = new NativePoint(clientX, clientY);
        if (!NativeMethods.ClientToScreen(target.Handle, ref point))
        {
            throw CreateWin32Exception("Não foi possível converter a coordenada da janela.");
        }

        await foregroundInput.ClickAsync(point.X, point.Y, cancellationToken);
    }

    private static async Task ActivateAsync(
        GameWindowTarget target,
        CancellationToken cancellationToken)
    {
        if (NativeMethods.IsIconic(target.Handle))
        {
            _ = NativeMethods.ShowWindow(target.Handle, SwRestore);
            await Task.Delay(350, cancellationToken);
        }

        if (!NativeMethods.SetForegroundWindow(target.Handle))
        {
            throw CreateWin32Exception(
                $"O Windows não permitiu ativar {target.Title}. Tente clicar no jogo uma vez.");
        }

        await Task.Delay(180, cancellationToken);
    }

    private static async Task PostKeyAsync(
        nint handle,
        ushort virtualKey,
        CancellationToken cancellationToken)
    {
        var scanCode = NativeMethods.MapVirtualKey(virtualKey, MapVkToVsc);
        var keyDownData = (nint)(1u | (scanCode << 16));
        var keyUpData = (nint)(1u | (scanCode << 16) | 0xC0000000u);

        Post(handle, WmKeyDown, virtualKey, keyDownData);
        await Task.Delay(70, cancellationToken);
        Post(handle, WmKeyUp, virtualKey, keyUpData);
    }

    private static async Task PostClickAsync(
        nint handle,
        int x,
        int y,
        CancellationToken cancellationToken)
    {
        var coordinates = (nint)((y << 16) | (x & 0xFFFF));
        Post(handle, WmMouseMove, 0, coordinates);
        Post(handle, WmLeftButtonDown, MkLeftButton, coordinates);
        await Task.Delay(70, cancellationToken);
        Post(handle, WmLeftButtonUp, 0, coordinates);
    }

    private static void ValidateWindow(GameWindowTarget target)
    {
        if (!NativeMethods.IsWindow(target.Handle))
        {
            throw new InvalidOperationException(
                $"A janela {target.Title} não existe mais. Atualize a lista de clientes.");
        }
    }

    private static void Post(nint handle, uint message, nuint wParam, nint lParam)
    {
        if (!NativeMethods.PostMessage(handle, message, wParam, lParam))
        {
            throw CreateWin32Exception("A mensagem direcionada não pôde ser enviada.");
        }
    }

    private static Win32Exception CreateWin32Exception(string message) =>
        new(Marshal.GetLastWin32Error(), message);

    [StructLayout(LayoutKind.Sequential)]
    private struct NativePoint(int x, int y)
    {
        public int X = x;
        public int Y = y;
    }

    private static class NativeMethods
    {
        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool IsWindow(IntPtr windowHandle);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool IsIconic(IntPtr windowHandle);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool ShowWindow(IntPtr windowHandle, int command);

        [DllImport("user32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool SetForegroundWindow(IntPtr windowHandle);

        [DllImport("user32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool ClientToScreen(IntPtr windowHandle, ref NativePoint point);

        [DllImport("user32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool PostMessage(
            IntPtr windowHandle,
            uint message,
            nuint wParam,
            nint lParam);

        [DllImport("user32.dll")]
        public static extern uint MapVirtualKey(uint code, uint mapType);
    }
}
