namespace BotNC.Core.Updates;

public interface IUpdateService
{
    Task<UpdateCheckResult> CheckAsync(
        Version currentVersion,
        CancellationToken cancellationToken);
}
