// Only this fixed aggregate is public. Never accept queries or project IDs from visitors.
export async function approvalTotal(fetchImpl = fetch, apiKey = process.env.POSTHOG_RO_API_KEY) {
  if (!apiKey) throw new Error('Approval count is not configured');
  const response = await fetchImpl('https://us.posthog.com/api/projects/417890/query/', {
    method: 'POST',
    headers: { authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
    body: JSON.stringify({
      query: {
        kind: 'HogQLQuery',
        query: "SELECT count() FROM events WHERE event = 'approve' AND properties.app_name = 'Automic Vault'",
      },
      name: 'Website human approval total',
    }),
    redirect: 'error',
    signal: AbortSignal.timeout(20000),
  });
  if (!response.ok) throw new Error(`PostHog query returned ${response.status}`);
  const data = await response.json();
  const total = data.results?.[0]?.[0];
  if (data.results?.length !== 1 || data.results[0]?.length !== 1 ||
      !Number.isSafeInteger(total) || total < 0) {
    throw new Error('Invalid approval count');
  }
  return total;
}
