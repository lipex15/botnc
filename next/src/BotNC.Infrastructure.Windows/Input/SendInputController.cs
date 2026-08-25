using System.ComponentModel;
using System.Runtime.InteropServices;
using BotNC.Core.Input;

namespace BotNC.Infrastructure.Windows.Input;

public sealed class SendInputController : IInputController
{
    private const uint InputMouse = 0;
    private const uint InputKeyboard = 1;
    private const uint MouseMove = 0x0001;
    private const uint MouseLeftDown = 0x0002;
    private const uint MouseLeftUp = 0x0004;
    private const uint MouseAbsolute = 0x8000;
    private const uint KeyUp = 0x0002;
    private const int SmCxScreen = 0;
    private const int SmCyScreen = 1;

    public Task MovePointerAsync(int x, int y, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        ValidatePoint(x, y);
        Send(CreateMouseInput(x, y, MouseMove | MouseAbsolute));
        return Task.CompletedTask;
    }

    public async Task ClickAsync(int x, int y, CancellationToken cancellationToken)
    {
        await MovePointerAsync(x, y, cancellationToken);
        Send(CreateMouseInput(x, y, MouseMove | MouseAbsolute | MouseLeftDown));
        await Task.Delay(70, cancellationToken);
        Send(CreateMouseInput(x, y, MouseMove | MouseAbsolute | MouseLeftUp));
    }

    public async Task PressKeyAsync(ushort virtualKey, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        Send(CreateKeyboardInput(virtualKey, 0));
        await Task.Delay(55, cancellationToken);
        Send(CreateKeyboardInput(virtualKey, KeyUp));
    }

    private static void ValidatePoint(int x, int y)
    {
        var width = NativeMethods.GetSystemMetrics(SmCxScreen);
        var height = NativeMethods.GetSystemMetrics(SmCyScreen);
        if (x < 0 || y < 0 || x >= width || y >= height)
        {
            throw new ArgumentOutOfRangeException(
                nameof(x),
                $"O ponto ({x}, {y}) está fora do monitor principal {width}×{height}.");
        }
    }

    private static NativeInput CreateMouseInput(int x, int y, uint flags)
    {
        var width = NativeMethods.GetSystemMetrics(SmCxScreen);
        var height = NativeMethods.GetSystemMetrics(SmCyScreen);
        var normalizedX = (int)Math.Round(x * 65535d / Math.Max(1, width - 1));
        var normalizedY = (int)Math.Round(y * 65535d / Math.Max(1, height - 1));

        return new NativeInput
        {
            Type = InputMouse,
            Union = new InputUnion
            {
                Mouse = new MouseInput
                {
                    Dx = normalizedX,
                    Dy = normalizedY,
                    Flags = flags
                }
            }
        };
    }

    private static NativeInput CreateKeyboardInput(ushort virtualKey, uint flags) =>
        new()
        {
            Type = InputKeyboard,
            Union = new InputUnion
            {
                Keyboard = new KeyboardInput
                {
                    VirtualKey = virtualKey,
                    Flags = flags
                }
            }
        };

    private static void Send(NativeInput input)
    {
        var inputs = new[] { input };
        var sent = NativeMethods.SendInput(
            (uint)inputs.Length,
            inputs,
            Marshal.SizeOf<NativeInput>());
        if (sent != inputs.Length)
        {
            throw new Win32Exception(Marshal.GetLastWin32Error(), "O SendInput falhou.");
        }
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct NativeInput
    {
        public uint Type;
        public InputUnion Union;
    }

    [StructLayout(LayoutKind.Explicit)]
    private struct InputUnion
    {
        [FieldOffset(0)] public MouseInput Mouse;
        [FieldOffset(0)] public KeyboardInput Keyboard;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct MouseInput
    {
        public int Dx;
        public int Dy;
        public uint MouseData;
        public uint Flags;
        public uint Time;
        public nuint ExtraInfo;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct KeyboardInput
    {
        public ushort VirtualKey;
        public ushort ScanCode;
        public uint Flags;
        public uint Time;
        public nuint ExtraInfo;
    }

    private static class NativeMethods
    {
        [DllImport("user32.dll", SetLastError = true)]
        public static extern uint SendInput(
            uint inputCount,
            [In] NativeInput[] inputs,
            int inputSize);

        [DllImport("user32.dll")]
        public static extern int GetSystemMetrics(int index);
    }
}
