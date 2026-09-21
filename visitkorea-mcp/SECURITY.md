# Security policy

Report suspected vulnerabilities privately to the repository owner rather
than opening a public issue. Do not include API keys, request URLs containing
`serviceKey`, or other credentials in reports.

The server validates user input, masks upstream credential errors, disables
HTTP access logs, and keeps stdio logs off stdout. Deploy public HTTP behind
the Node proxy or another authenticated, rate-limited gateway.
