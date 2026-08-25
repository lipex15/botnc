namespace BotNC.Core.Windows;

public sealed record GameWindowTarget(
    nint Handle,
    string Title,
    int ProcessId,
    bool IsMinimized,
    bool IsVisible)
{
    public string DisplayName => IsMinimized ? $"{Title} · minimizado" : Title;

    public override string ToString() => DisplayName;
}
