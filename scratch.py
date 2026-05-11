import re

message_text = "📉 *TRM Oficial - 2026-05-07*\n\n💵 Valor: $3,706.44 COP (- $16.89). Fuente: www.superfinanciera.gov.co"
msg_snippet = re.sub(r'\s+', ' ', re.sub(r'[^\x00-\x7F]+', '', message_text[:100])).strip().replace("*", "")

print(f"msg_snippet: {repr(msg_snippet)}")
