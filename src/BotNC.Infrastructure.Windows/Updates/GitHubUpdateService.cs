using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json.Serialization;
using BotNC.Core.Updates;

namespace BotNC.Infrastructure.Windows.Updates;

public sealed class GitHubUpdateService(HttpClient httpClient) : IUpdateService
{
    private static readonly Uri LatestReleaseUri =
        new("https://api.github.com/repos/lipex15/botnc/releases/latest");

    public async Task<UpdateCheckResult> CheckAsync(
        Version currentVersion,
        CancellationToken cancellationToken)
    {
        using var request = new HttpRequestMessage(HttpMethod.Get, LatestReleaseUri);
        request.Headers.UserAgent.Add(new ProductInfoHeaderValue("BotNC", currentVersion.ToString()));
        request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/vnd.github+json"));

        using var response = await httpClient.SendAsync(request, cancellationToken);
        if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            return new UpdateCheckResult(
                false,
                currentVersion,
                null,
                null,
                "Ainda não existe uma versão publicada no GitHub Releases.");
        }

        response.EnsureSuccessStatusCode();
        var release = await response.Content.ReadFromJsonAsync<GitHubRelease>(
            cancellationToken: cancellationToken);
        if (release is null || !TryParseVersion(release.TagName, out var latestVersion))
        {
            return new UpdateCheckResult(
                false,
                currentVersion,
                null,
                null,
                "O GitHub respondeu, mas a versão publicada não pôde ser interpretada.");
        }

        var available = latestVersion > currentVersion;
        var page = Uri.TryCreate(release.HtmlUrl, UriKind.Absolute, out var releasePage)
            ? releasePage
            : null;

        return new UpdateCheckResult(
            available,
            currentVersion,
            latestVersion,
            page,
            available
                ? $"A versão {latestVersion} está disponível."
                : "Você já está usando a versão mais recente.");
    }

    private static bool TryParseVersion(string tag, out Version version) =>
        Version.TryParse(tag.TrimStart('v', 'V'), out version!);

    private sealed record GitHubRelease(
        [property: JsonPropertyName("tag_name")] string TagName,
        [property: JsonPropertyName("html_url")] string HtmlUrl);
}
