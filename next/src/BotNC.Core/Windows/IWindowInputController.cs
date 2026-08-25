namespace BotNC.Core.Windows;

public interface IWindowInputController
{
    Task SendKeyAsync(
        GameWindowTarget target,
        ushort virtualKey,
        WindowInputMode mode,
        CancellationToken cancellationToken);

    Task SendClickAsync(
        GameWindowTarget target,
        int clientX,
        int clientY,
        WindowInputMode mode,
        CancellationToken cancellationToken);
}
