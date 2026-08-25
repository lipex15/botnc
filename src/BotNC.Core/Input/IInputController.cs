namespace BotNC.Core.Input;

public interface IInputController
{
    Task MovePointerAsync(int x, int y, CancellationToken cancellationToken);
    Task ClickAsync(int x, int y, CancellationToken cancellationToken);
    Task PressKeyAsync(ushort virtualKey, CancellationToken cancellationToken);
}
