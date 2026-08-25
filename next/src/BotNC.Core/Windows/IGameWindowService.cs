namespace BotNC.Core.Windows;

public interface IGameWindowService
{
    Task<IReadOnlyList<GameWindowTarget>> DiscoverAsync(CancellationToken cancellationToken);
}
