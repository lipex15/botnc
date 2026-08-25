using System.Runtime.InteropServices;
using System.Text;
using BotNC.Core.Windows;

namespace BotNC.Infrastructure.Windows.Windows;

public sealed class GameWindowService : IGameWindowService
{
    private static readonly HashSet<string> SupportedTitles =
        new(StringComparer.Ordinal)
        {
            "NIGHT CROWS(1)",
            "NIGHT CROWS(2)"
        };

    public Task<IReadOnlyList<GameWindowTarget>> DiscoverAsync(
        CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        var windows = new List<GameWindowTarget>();

        NativeMethods.EnumWindows(
            (handle, _) =>
            {
                if (cancellationToken.IsCancellationRequested)
                {
                    return false;
                }

                var title = ReadTitle(handle);
                if (!SupportedTitles.Contains(title))
                {
                    return true;
                }

                NativeMethods.GetWindowThreadProcessId(handle, out var processId);
                windows.Add(
                    new GameWindowTarget(
                        handle,
                        title,
                        checked((int)processId),
                        NativeMethods.IsIconic(handle),
                        NativeMethods.IsWindowVisible(handle)));
                return true;
            },
            IntPtr.Zero);

        cancellationToken.ThrowIfCancellationRequested();
        IReadOnlyList<GameWindowTarget> result = windows
            .OrderBy(window => window.Title, StringComparer.Ordinal)
            .ToArray();
        return Task.FromResult(result);
    }

    private static string ReadTitle(IntPtr handle)
    {
        var length = NativeMethods.GetWindowTextLength(handle);
        if (length <= 0)
        {
            return string.Empty;
        }

        var buffer = new StringBuilder(length + 1);
        _ = NativeMethods.GetWindowText(handle, buffer, buffer.Capacity);
        return buffer.ToString().Trim();
    }

    private static class NativeMethods
    {
        public delegate bool EnumWindowsCallback(IntPtr windowHandle, IntPtr parameter);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool EnumWindows(EnumWindowsCallback callback, IntPtr parameter);

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        public static extern int GetWindowText(
            IntPtr windowHandle,
            StringBuilder text,
            int maximumCount);

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        public static extern int GetWindowTextLength(IntPtr windowHandle);

        [DllImport("user32.dll")]
        public static extern uint GetWindowThreadProcessId(
            IntPtr windowHandle,
            out uint processId);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool IsIconic(IntPtr windowHandle);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool IsWindowVisible(IntPtr windowHandle);
    }
}
