// Target IP specified for custom domain routing
const TARGET_IP: string = "159.195.17.92";

interface DNSAnswer {
  name: string;
  type: number;
  TTL: number;
  data: string;
}

interface CloudflareDNSResponse {
  Status: number;
  TC: boolean;
  RD: boolean;
  RA: boolean;
  AD: boolean;
  CD: boolean;
  Question: Array<{ name: string; type: number }>;
  Answer?: DNSAnswer[];
}

/**
 * Copies the target IP to clipboard
 */
export function copyIp(): void {
  const ip = document.getElementById("ipVal")?.textContent?.trim() || TARGET_IP;
  navigator.clipboard.writeText(ip).then(() => {
    const btn = document.querySelector(".copy-btn") as HTMLButtonElement | null;
    if (btn) {
      const originalText = btn.textContent;
      btn.textContent = "✓ Copied!";
      setTimeout(() => {
        btn.textContent = originalText;
      }, 2000);
    }
  }).catch((err) => {
    console.error("Clipboard copy failed:", err);
  });
}

/**
 * Queries DNS over HTTPS using Cloudflare's public resolver
 */
async function queryDNS(domain: string): Promise<string[]> {
  const cleanDomain = domain.replace(/^https?:\/\//i, '').split('/')[0].trim();
  const url = `https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(cleanDomain)}&type=A`;
  
  const response = await fetch(url, {
    headers: {
      "Accept": "application/dns-json"
    }
  });

  if (!response.ok) {
    throw new Error(`DNS resolution failed with status ${response.status}`);
  }

  const json: CloudflareDNSResponse = await response.json();
  if (!json.Answer || json.Answer.length === 0) {
    return [];
  }

  // Type 1 corresponds to DNS 'A' record
  return json.Answer.filter(ans => ans.type === 1).map(ans => ans.data);
}

/**
 * Initializes the interactive form and handlers
 */
function init(): void {
  const form = document.getElementById("checkerForm") as HTMLFormElement | null;
  const input = document.getElementById("domainInput") as HTMLInputElement | null;
  const resultDiv = document.getElementById("checkResult") as HTMLDivElement | null;
  const btn = document.getElementById("checkBtn") as HTMLButtonElement | null;

  // Make copyIp available on window for inline click
  (window as unknown as { copyIp: typeof copyIp }).copyIp = copyIp;

  if (!form || !input || !resultDiv || !btn) return;

  form.addEventListener("submit", async (e: Event) => {
    e.preventDefault();
    const domain = input.value.trim();
    if (!domain) return;

    btn.disabled = true;
    btn.textContent = "Checking DNS...";
    resultDiv.style.display = "block";
    resultDiv.className = "result-pending";
    resultDiv.textContent = `Resolving DNS 'A' records for ${domain}...`;

    try {
      const ips = await queryDNS(domain);

      if (ips.length === 0) {
        resultDiv.className = "result-pending";
        resultDiv.innerHTML = `⚠️ <strong>No 'A' records found for <code>${domain}</code>.</strong><br>If you just added the record, wait a few minutes for DNS propagation and try again.`;
      } else if (ips.includes(TARGET_IP)) {
        resultDiv.className = "result-success";
        resultDiv.innerHTML = `✅ <strong>Success!</strong> <code>${domain}</code> is pointed to <code>${TARGET_IP}</code>.<br>Your site is ready! Visit <a href="http://${domain}" target="_blank" style="color: #58a6ff; text-decoration: underline;">http://${domain}</a>.`;
      } else {
        resultDiv.className = "result-error";
        resultDiv.innerHTML = `❌ <strong>Mismatch detected.</strong><br>Found A record: <code>${ips.join(', ')}</code>.<br>Expected: <code>${TARGET_IP}</code>. Please update your DNS settings.`;
      }
    } catch (err: unknown) {
      resultDiv.className = "result-error";
      const message = err instanceof Error ? err.message : String(err);
      resultDiv.innerHTML = `❌ <strong>Error checking domain:</strong> ${message}`;
    } finally {
      btn.disabled = false;
      btn.textContent = "Check DNS Status";
    }
  });
}

document.addEventListener("DOMContentLoaded", init);
