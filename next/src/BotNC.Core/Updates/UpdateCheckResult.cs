namespace BotNC.Core.Updates;

public sealed record UpdateCheckResult(
    bool IsAvailable,
    Version CurrentVersion,
    Version? LatestVersion,
    Uri? ReleasePage,
    string Message);
