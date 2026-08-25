namespace BotNC.Core.Capture;

public sealed record CapturedFrame(
    int Width,
    int Height,
    int Stride,
    ReadOnlyMemory<byte> BgraPixels,
    DateTimeOffset CapturedAt);
