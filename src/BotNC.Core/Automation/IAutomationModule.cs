namespace BotNC.Core.Automation;

public interface IAutomationModule
{
    string Id { get; }
    string DisplayName { get; }
    string Description { get; }
    AutomationModuleState State { get; }

    Task StartAsync(CancellationToken cancellationToken);
    Task StopAsync(CancellationToken cancellationToken);
}
