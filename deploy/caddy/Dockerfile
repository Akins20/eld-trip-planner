# Caddy with the DuckDNS DNS-01 plugin: obtains Let's Encrypt certs via a DNS TXT
# record (the DuckDNS token), so it needs no inbound ports 80/443. It terminates
# TLS on a non-standard port and reverse-proxies to the API container.
FROM caddy:2-builder AS builder
RUN xcaddy build --with github.com/caddy-dns/duckdns

FROM caddy:2
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
COPY Caddyfile /etc/caddy/Caddyfile
