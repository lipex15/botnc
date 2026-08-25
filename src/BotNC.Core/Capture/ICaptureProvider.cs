namespace BotNC.Core.Capture;

public interface ICaptureProvider
{
    string Name { get; }
    ValueTask<CapturedFrame> CapturePrimaryScreenAsync(CancellationToken cancellationToken);
}
