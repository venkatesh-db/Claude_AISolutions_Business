# Near-miss: wrong test target led to a wrong conclusion

**Severity:** none shipped — caught before the release decision
**Where:** during the live `safe-release` run for the GZip-compression change

## What happened

Stage 8 (repeat and compare) checked whether the new GZip compression
middleware was active by requesting `/metrics` with
`Accept-Encoding: gzip` and looking for a `Content-Encoding` response
header. It was absent on both the pre-change and post-change containers.
The first-draft conclusion was "the change had no effect."

## Why that conclusion was wrong

`/metrics` returns a 75-byte JSON body. `GZipMiddleware` only compresses
responses at or above `minimum_size=500` bytes by design — the endpoint
tested was structurally incapable of ever showing the effect being
tested for, independent of whether the middleware worked.

## How it was caught

Before writing up "no effect" as a finding, the response size was
checked (`curl ... | wc -c` → 75 bytes). Re-tested against
`/openapi.json` (3,219 bytes) — `Content-Encoding: gzip` appeared
exactly as expected on the post-change container and not on the
pre-change one.

## Root cause

The test-target endpoint was chosen without checking whether it could
structurally exhibit the effect under test. "The change appears to have
had no effect" and "the change had no effect" are different claims, and
only checking response size distinguished them.

## Prevention

`agents/execution/AGENT.md` and `tools/` should default to testing
against the largest available response, or explicitly document the
target's typical size when a specific endpoint is required — not assume
any endpoint is a valid probe for any change.
