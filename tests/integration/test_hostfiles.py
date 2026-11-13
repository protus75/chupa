"""Core renderer contract; regenerate the golden with uv run python -m tests.test_hostfiles."""

import asyncio
import base64
import builtins
import re
from pathlib import Path

import pytest

from chupa import hostfiles
from chupa.seams import LocalFileSystem
from tests.integration.test_cli import root
from tests.integration.test_git import commit_lock
from tests.integration.test_merge import repo
from tests.integration.test_stages import agent, verdict

REPO = Path(__file__).resolve().parents[2]
GOLDEN = b"PCEtLSBjaHVwYTpjb3JlIGJlZ2luIC0tPgojIyBUaWNrZXQgYXV0aG9yaW5nIC0tIHJlYWQgYmVmb3JlIHdyaXRpbmcgYW55IHRpY2tldAoKVGhlc2UgcnVsZXMgY29tZSBmaXJzdCBiZWNhdXNlIHNlc3Npb25zIHRoYXQgc2tpbSBtaXNzIHRoZW0uIEhBUkQgcnVsZXMgaGF2ZSBubyBleGNlcHRpb25zLiBUaGV5IGFyZSBiZWhhdmlvcmFsOiBubyBnYXRlIGNhbiBqdWRnZSB0aGVtLCBzbyBuZXZlciBmaWxlIGFuIGVuZm9yY2VtZW50IHRpY2tldCBmb3Igb25lLgoKLSBIQVJEOiBJbiBhbiBpbnRlcmFjdGl2ZSBjaGF0LCBldmVyeSByZXF1ZXN0ZWQgY2hhbmdlIHRvIHJlcG8gY29udGVudCAoY29kZSwgZG9jcywgQ0xBVURFLm1kLCBBR0VOVFMubWQsIHNldHRpbmdzLCBob29rcywgc2NyaXB0cywgY29uZmlnLCBhZ2VudCBydWxlcykgYmVjb21lcyBhIGRyYWZ0ZWQgdGlja2V0IGF0IGB0aWNrZXRzLzxzdGVtPi90aWNrZXQubWRgLCB0aGVuIHN0b3AuIE5ldmVyIGVkaXQgb3IgY29tbWl0IG9uIG1haW4uIFRoZSBvbmx5IGV4Y2VwdGlvbnM6ICgxKSB0aGUgdXNlciBzYXlzICJlZGl0IG1haW4iLCAiY29tbWl0IGRpcmVjdGx5IiwgInNraXAgdGhlIHRpY2tldCIsICJkbyBpdCBpbmxpbmUiLCBvciBhbiBlcXVhbGx5IGV4cGxpY2l0IG92ZXJyaWRlIHRoaXMgdHVybjsgYW5nZXIgd29yZHMgYWxvbmUgZG8gbm90IGNvdW50OyAoMikgeW91IGFyZSBpbiBhIGNodXBhIHRpY2tldCB3b3JrdHJlZTsgKDMpIHRoZSB1c2VyIG5hbWVzIGJ5IHBhdGggYSBmaWxlIHVuZGVyIGFuIGV4aXN0aW5nIGB0aWNrZXRzLzxzdGVtPi9gIHRvIGVkaXQgb3IgZGVsZXRlOyAoNCkgcmVhZC1vbmx5IGluc3BlY3Rpb247ICg1KSB0aGUgc3VwZXJ2aXNpbmcgZml4ZXMgYmVsb3cuIElmIHlvdSBhbHJlYWR5IGVkaXRlZCBtYWluIHdpdGhvdXQgYW4gb3ZlcnJpZGUsIHN0b3AsIHNheSBzbywgYW5kIGFzayB3aGV0aGVyIHRvIHJldmVydCBhbmQgcmVmaWxlLiBXaHk6IGNoYXQgZWRpdHMgc2tpcCB0aGUgdGlja2V0LCBydW4gcmVjb3JkLCByZXZpZXcsIGFuZCByZXRybyB0aGF0IG1ha2UgY2h1cGEgZGVidWdnYWJsZS4KLSBIQVJEOiBOZXZlciB3cml0ZSBhIHRpY2tldCBmcm9tIG1lbW9yeS4gUnVuIGBjaHVwYSBuZXcgPHN0ZW0+IC0ta2luZCBmZWF0dXJlfGJ1Z3xjaG9yZWA7IGl0IHdyaXRlcyB0aGUgc2tlbGV0b24gYW5kIHByaW50cyB0aGUgcGF0aCBvZiB0aGUgdGlja2V0IGF1dGhvcmluZyBndWlkZSBpbiB5b3VyIGNodXBhIGluc3RhbGwgKGZvciBhbiBleGlzdGluZyB0aWNrZXQsIGl0cyByZWZ1c2FsIHByaW50cyB0aGUgc2FtZSBwYXRoKS4gUmVhZCB0aGF0IGxvY2FsIGZpbGUgaW4gZnVsbC4gYGNodXBhIGRvY3NgIHByaW50cyB0aGUgaW5zdGFsbGVkIHBhdGhzIG9mIGFsbCBob3N0IGd1aWRlcyAoYXV0aG9yaW5nLCBydW5uaW5nLCBjb25maWcgY29udHJhY3QpOyByZWFkIHRoZW0gbG9jYWxseSwgbmV2ZXIgZnJvbSBhIFVSTC4gRmlsbCBldmVyeSBzZWN0aW9uLCBydW4gYGNodXBhIGxpbnQgPHN0ZW0+YCB1bnRpbCBpdCBleGl0cyAwLCB0aGVuIHJ1biBgY2h1cGEgcmV2aWV3IDxzdGVtPmAgYW5kIHJlcGFpciBldmVyeSBmaW5kaW5nIHVudGlsIGl0IHByaW50cyBhcHByb3ZlLiBUaWNrZXRzIGFyZSBtYXJrZG93biBmaWxlcywgbmV2ZXIgaXNzdWUtdHJhY2tlciBpdGVtcy4gV2h5OiBzdGFsZSB0aWNrZXQgc2hhcGVzIGJyZWFrIHJ1bnMgYmVmb3JlIGltcGxlbWVudGF0aW9uIHN0YXJ0cy4KLSBGZW5jZSBldmVyeSBmaWxlIHRoZSBjaGFuZ2UgZm9yY2VzLCBpbmNsdWRpbmcgY2FsbGVycywgaW1wb3J0ZXJzLCBkb2N1bWVudHMgaXQgY2hhbmdlcywgYW5kIHRlc3RzIHRoYXQgcGluIGEgY2hhbmdlZCBuYW1lLCB2YWx1ZSwgb3IgdmVyc2lvbi4gV2h5OiBhIGZvcmNlZCBmaWxlIG91dHNpZGUgdGhlIGZlbmNlIG1ha2VzIHRoZSB0aWNrZXQgaW1wb3NzaWJsZS4KLSBGcm9udG1hdHRlciBob2xkcyBvbmx5IGZpZWxkcyByZWFkIGJ5IHNjaGVkdWxpbmcsIGdhdGVzLCBvciBhdXRob3JpbmcvdHJpYWdlIHBvbGljeS4gYCMjIERlcGVuZHMgb25gIG5hbWVzIG9ubHkgYSB0aWNrZXQgd2hvc2UgbWVyZ2VkIGNvZGUgdGhpcyBvbmUgbmVlZHM7IHB1dCBhbGwgb3RoZXIgb3JkZXJpbmcgaW4gcHJpb3JpdHkgb3IgYCMjIFJ1bnMgYmVmb3JlYCwgbmV2ZXIgaW4gcHJvc2UuIFdoeTogYSBkZXBlbmRzIHVzZWQgZm9yIG9yZGVyaW5nIGJsb2NrcyB0aGUgcXVldWUgd2hlbiB0aGUgZmlyc3QgdGlja2V0IGZhaWxzLgotIEhBUkQ6IFdoZW4gYSByZXBvcnRlZCBwcm9ibGVtIGhhcyBhIGNhdXNlIHRoYXQgd2lsbCByZWN1ciwgd3JpdGUgdHdvIHNlcGFyYXRlIHRpY2tldHMgaW4gdGhlIHNhbWUgdHVybi4gRmlyc3QgdGhlIGluc3RhbmNlIGZpeDogbWluaW1hbCBzY29wZSwgd3JpdHRlbiBiZWZvcmUgYW55IGNhdXNlIGRpYWdub3Npcy4gVGhlbiB0aGUgY2F1c2UgZml4LCBuZXZlciBmb2xkZWQgaW50byB0aGUgaW5zdGFuY2U7IHRoZSB0dXJuIGlzIHVuZmluaXNoZWQgdW50aWwgaXQgZXhpc3RzLiBCb3RoIGFyZSBzb2xpY2l0ZWQsIHNvIG5vIGFzayBpcyBuZWVkZWQuIFJvdXRpbmc6CiAgLSBQcm9kdWN0IGluc3RhbmNlOiBgcHJpb3JpdHk6IFAwYCwgbm8gYmxvY2tpbmcgZGVwZW5kcy4KICAtIFByb2R1Y3QgY2F1c2UgKGluZXJ0OyBkb2VzIG5vdCBzcHJlYWQgb24gaXRzIG93bik6IGBwcmlvcml0eTogUDFgLiBXaGVuIHRoZSB0d28gc2hhcmUgYW4gZWRpdCBzdXJmYWNlLCB0aGUgaW5zdGFuY2UgbGlzdHMgdGhlIGNhdXNlIGluIGAjIyBSdW5zIGJlZm9yZWAuCiAgLSBPcmNoZXN0cmF0aW9uIGNhdXNlIChzY2hlZHVsZXIsIGdhdGUsIGVudmlyb25tZW50LCBzaGFyZWQgbW9kdWxlLCBmaXh0dXJlIGZvcm1hdDsga2VlcHMgYnJlYWtpbmcgcnVucyB3aGlsZSBpdCBzaXRzKTogYHByaW9yaXR5OiBQMGAsIGAjIyBSdW5zIGJlZm9yZWAgZXZlcnkgdGlja2V0IGl0IHVuYmxvY2tzLCBuZXZlciBkZXBlbmRzIG9uIGEgcHJvZHVjdCBpbnN0YW5jZS4KLSBIQVJEOiBGb3IgdGlja2V0LXdvcnRoeSB3b3JrIHRoZSB1c2VyIGRpZCBub3QgYXNrIGZvciAoZm9sbG93LXVwLCBwcmV2ZW50aW9uLCBlbmZvcmNlbWVudCBsaW50LCBzd2VlcCksIHN0b3AgYmVmb3JlIGRpdmluZzogbmFtZSBpdCBpbiAxLTIgc2VudGVuY2VzIGFuZCBhc2sgdGhlIHVzZXIgdG8gY2hvb3NlIGF1dGhvciBub3csIGFmdGVyIHRoZSBjdXJyZW50IHRhc2ssIG9yIHNraXAuICJBZnRlciIgbWFrZXMgaXQgYW4gb3BlbiB0aHJlYWQuIEFubm91bmNlIGluIG9uZSBsaW5lIGFueSB1bnNvbGljaXRlZCBpbnZlc3RpZ2F0aW9uIGxvbmdlciB0aGFuIGEgY291cGxlIG9mIG1pbnV0ZXMuIFRoZSB1c2VyJ3MgcmVxdWVzdGVkIHRhc2sgYWx3YXlzIGdvZXMgZmlyc3QuIEF1dG9ub21vdXMgcnVucyBza2lwIHRoZSBhc2sgYW5kIGZpbGUgdG8gdGhlIFN1Z2dlc3Rpb24gQm94LgotIEZpbGUgYW4gdW5yZXF1ZXN0ZWQgaWRlYSBvciBzZWNvbmQgcHJvYmxlbSB3aXRoIGBjaHVwYSBzdWdnZXN0ICI8c3VtbWFyeT4iYCBhbmQgbmFtZSBpdCBpbiBvbmUgbGluZS4gV2h5OiBhIG1hcmdpbiBzdWdnZXN0aW9uIGRpZXMgd2l0aCB0aGUgY2hhdC4KLSBBIHN1cGVydmlzaW5nIHNlc3Npb24gbWF5LCB1bmFza2VkLCBmaXggYSB0aWNrZXQncyBsaW50IG9yIGZvcm1hdCBlcnJvcnMsIGFkZCBhIGZpbGUgbWlzc2luZyBmcm9tIGAjIyBTY29wZSBmZW5jZWAgb3IgYCMjIENvbnRleHRgLCBjb3JyZWN0IGEgc3RhbGUgcGF0aCwgbWFrZSBhIHNpbXBsZSB3b3JkaW5nIHVwZGF0ZSwgYW5kIHJ1biBvciByZXN0YXJ0IHRoZSBkcmFpbi4gSXQgbWF5IG5vdCBjb25maXJtIG9yIHJlamVjdCwgcmV0cnkgYSBzdGVtIHdob3NlIGNhcHMgYXJlIHNwZW50LCBlZGl0IGEgcnVubmluZyB0aWNrZXQsIGNoYW5nZSBhIHRpY2tldCdzIGdvYWwgb3Igc2NvcGUsIG9yIHJld3JpdGUgYSB0aWNrZXQgdGhlIGVuZ2luZSBhdXRob3JlZDsgdGhvc2UgZ28gdG8gdGhlIHVzZXIuCgojIyBEaWFnbm9zaXMKCi0gSEFSRDogV2hlbiBhIHJ1biBmYWlscywgaXMga2lsbGVkLCB0aW1lcyBvdXQsIHN0YWxscywgb3IgZXNjYWxhdGVzLCBuYW1lIGl0cyByb290IGNhdXNlIGluIG9uZSBzZW50ZW5jZSBiZWZvcmUgZWRpdGluZyBzcGVjIG9yIGNvZGUgb3IgcmVydW5uaW5nLiBSZWFkIGBjaHVwYSBzdGF0dXNgLCBgdGlja2V0cy88c3RlbT4vYCAoYHJ1bi5tZGAsIGBjaGVja3MuanNvbmAsIGBkaWFnbm9zaXMuanNvbmAsIGByZXZpZXcubWRgLCBgYXR0ZW1wdHMvYCksIGFuZCB0aGUgZW5naW5lIGxvZy4gRml4IHRoZSBjYXVzZSB3aGVyZSBpdCBsaXZlcy4gQW4gZXh0ZXJuYWwgY2F1c2UgKGVuZ2luZSwgZ2F0ZSwgZW52aXJvbm1lbnQsIHNoYXJlZCBtb2R1bGUsIGZpeHR1cmUsIGZsYWt5IHRlc3QsIHdyb25nIHByZW1pc2UpIGlzIGZpeGVkIGZpcnN0IGFuZCBvcmRlcmVkIGFoZWFkIHdpdGggcHJpb3JpdHkgYW5kIGAjIyBSdW5zIGJlZm9yZWAuIERvIG5vdCBhc3N1bWUgdGhlIHRpY2tldCBpcyB3cm9uZy4gTmV2ZXIgcmVydW4gYSBmbGFreSBmYWlsdXJlIHVudGlsIGl0IHBhc3NlcyBhbmQgY2FsbCB0aGF0IGZpeGVkLgotIEhBUkQ6IFdoZW4gYSBzeW1wdG9tIHJlY3VycyBvbiBhIHN1cmZhY2UgYWxyZWFkeSBmaXhlZCwgbmFtZSB0aGUgcm9vdCBtb2RlbCBhZ2FpbnN0IHRoZSBjYW5vbmljYWwgc3BlYyAoZGVzaWduIGRvY3MsIGNvbnRyYWN0cykgYW5kIHdyaXRlIGEgcm9vdC1jYXVzZSB0aWNrZXQsIG5vdCBhbm90aGVyIHBhdGNoLiBBIHNjb3BlIGZlbmNlIHRoYXQgZm9yYmlkcyB0b3VjaGluZyB0aGUgc3VzcGVjdGVkIHJvb3QgaXMgYSByZWQgZmxhZzogcmUtc2NvcGUgaXQuIFRlc3RzIHRoYXQgYXNzZXJ0IHRoZSBjdXJyZW50IHdyb25nIGJlaGF2aW9yIHByb3ZlIG5vdGhpbmcuIE5ldmVyIHdyaXRlICJ0aGUgZGVmZWN0IHdhcyBub3QgWCIgd2l0aG91dCBjaGVja2luZyB0aGUgc3BlYy4KLSBIQVJEOiBXaXRoIGV2ZXJ5IGZpeCBvciBkaWFnbm9zaXMsIG5hbWUgdGhlIGNoYW5nZSB0aGF0IHN0b3BzIHRoZSB3aG9sZSBjbGFzcyBmcm9tIHJlY3VycmluZyAocnVsZSwgbGludCwgZ2F0ZSwgdGVtcGxhdGUgZGVmYXVsdCwgZ2VuZXJhdG9yKSBhcyBhIHNlcGFyYXRlIGl0ZW0uIENoZWFwIGFuZCBpbiBzY29wZTogZG8gaXQgdW5kZXIgdGhlIHNhbWUgYXV0aG9yaXphdGlvbi4gQ2hlYXAgYnV0IG91dCBvZiBzY29wZTogbmFtZSBpdCwgdGhlbiBmb2xsb3cgdGhlIGFzayBmb3IgdW5yZXF1ZXN0ZWQgd29yay4gRXhwZW5zaXZlIG9yIHVuY2VydGFpbjogYGNodXBhIHN1Z2dlc3RgLiBTdGF5aW5nIHNpbGVudCBpcyB0aGUgZmFpbHVyZS4KCi0gSEFSRDogQSBmaXggdGhhdCBiZWxvbmdzIGluIGNodXBhIChhIHByb21wdCBzcGVjLCBnYXRlLCB0aWNrZXQgZm9ybWF0LCBob3N0IGd1aWRlLCBvciB0aGlzIGJsb2NrKSBpcyBuZXZlciBjb3BpZWQgb3IgcGF0Y2hlZCBpbnRvIGhvc3QgZmlsZXMuIFJlcG9ydCBpdCBmb3IgdGhlIG93bmVyIHRvIGNhcnJ5IHRvIGNodXBhLCB0aGVuIHN0b3AuIFdoeTogYSBob3N0IGNvcHkgY29tcGV0ZXMgd2l0aCBjaHVwYSdzIHJ1bGUsIHJlYWNoZXMgbm8gb3RoZXIgaG9zdCwgYW5kIGdvZXMgc3RhbGUgb24gdXBncmFkZS4KCiMjIENoYXQgc2Vzc2lvbiBjb25kdWN0CgpUaGVzZSBydWxlcyBnb3Zlcm4gaW50ZXJhY3RpdmUgY2hhdCB3aXRoIHRoZSBvd25lciBwcmVzZW50LiBUaWNrZXQgYWdlbnRzIHNraXAgdGhpcyBzZWN0aW9uLgoKLSBIQVJEOiBXaGVuIGEgcmVwbHkgcmFpc2VzIG1vcmUgdGhhbiBvbmUgcXVlc3Rpb24sIG9wdGlvbiwgb3IgbmV4dCBzdGVwLCB5b3Ugb3duIHRoYXQgbGlzdCBvZiBvcGVuIHRocmVhZHMuIEFjdGluZyBvbiBvbmUgbmV2ZXIgY2xvc2VzIHRoZSBvdGhlcnMuIEVuZCBlYWNoIHJlcGx5IHdpdGggYSBgU3RpbGwgb3BlbjpgIGxpc3QgdW50aWwgdGhlIHVzZXIgcmVzb2x2ZXMgZWFjaCBvbmUgb3IgeW91IGNvbXBsZXRlIGl0IGFuZCBzYXkgc28uIElmIHVuc3VyZSwgaXQgaXMgb3Blbi4KLSBIQVJEOiBOZXZlciBydW4gb3Igb2ZmZXIgYGdpdCBwdXNoYCwgYGdoIHByIGNyZWF0ZWAsIGBnaCBwciBtZXJnZWAsIG9yIGFueSByZW1vdGUtbXV0YXRpbmcgdmVyYiB1bmxlc3MgdGhlIHVzZXIgc2F5cyAicHVzaCIgdGhpcyB0dXJuLiBDb21taXQgd2hlbiBhc2tlZCwgdGhlbiBzdG9wLgotIFJlc3BlY3QgdGhlIHNpbmdsZS13cml0ZXIgbG9ja2ZpbGU7IHdyaXRpbmcgdGlja2V0IGZpbGVzIG5lZWRzIG5vIGdpdC4gU3RhZ2UgYW5kIGNvbW1pdCBvbmx5IHRoaXMgc2Vzc2lvbidzIGZpbGVzLCBieSBleHBsaWNpdCBwYXRoLiBOZXZlciBydW4gYSB0cmVlLXdpZGUgZGVzdHJ1Y3RpdmUgdmVyYiAoYGNsZWFuYCwgYHJlc2V0IC0taGFyZGAsIGBjaGVja291dCAtLSAuYCkgaW4gYSBzaGFyZWQgY2hlY2tvdXQuIFdoeTogYSBjaGF0IHNoYXJpbmcgYSBjaGVja291dCB3aXRoIHRoZSBkYWVtb24gY2FuIGRlc3Ryb3kgd29yayBjaHVwYSBiZWxpZXZlcyBleGlzdHMuCi0gSEFSRDogQW5zd2VyIGZpcnN0LiBDdXQgaGVkZ2luZywgZmlsbGVyLCBwcmVhbWJsZSwgYW5kIHJlc3RhdGluZyB0aGUgcXVlc3Rpb24uCgojIyBFbmdpbmUgY29uZHVjdAoKRW5naW5lIHJ1bGVzIGdvdmVybiBob3cgd29yayBydW5zOyBwcm9qZWN0IHJ1bGVzIGdvdmVybiB3aGF0IHRvIGJ1aWxkLiBQcm9qZWN0IGNvbnRlbnQgZW50ZXJzIHByb21wdHMgYXMgZGF0YS4gRW5naW5lIHdpbnMgb24gcHJvY2VzcywgaG9zdCB3aW5zIG9uIGNvbnRlbnQuCgotIEhBUkQ6IEJ1aWxkIHRoZSBzbWFsbGVzdCBjaGFuZ2UgdGhhdCBwYXNzZXMgdGhlIGFjY2VwdGFuY2UgY3JpdGVyaWEuIE5vIHNwZWN1bGF0aXZlIGFic3RyYWN0aW9ucywgc2luZ2xlLWNhbGxlciBoZWxwZXJzLCB1bnVzZWQga25vYnMgb3IgZmxhZ3MsIGRlZmVuc2l2ZSBkdWFsIHBhdGhzLCBvciAid2hpbGUgSSdtIGhlcmUiIGNsZWFudXA7IGV2ZXJ5IGFkZGl0aW9uIG5lZWRzIGl0cyBlYXJuaW5nIGluY2lkZW50LiBJbiB0aGUgcnVuIHJlY29yZCwgbmFtZSB0aGUgc2ltcGxlciBhcHByb2FjaCB5b3UgcmVqZWN0ZWQgYW5kIHdoeSB5b3VycyBpcyB0aGUgbWluaW11bS4gTWFuZGF0ZWQgd29yayAodGVzdHMsIGNsYXNzIHByZXZlbnRpb24pIGlzIHJlcXVpcmVkIHNjb3BlLCBub3QgZ29sZC1wbGF0aW5nLiBXaHk6IGFjY3JldGlvbiBpcyB0aGUgcHJpbWFyeSBmYWlsdXJlIG1vZGUuCi0gTmV2ZXIgaGFuZC1lZGl0IHRoaXMgbWFuYWdlZCBibG9jazsgY2hhbmdlIHRoZSBlbmdpbmUgdGVtcGxhdGUgYW5kIHJ1biBjaHVwYSBjb3JlIHRvIHJlZnJlc2ggaXQuIFdoeTogdGhlIG5leHQgcmVuZGVyIG92ZXJ3cml0ZXMgZWRpdHMuCi0gQ29tbWl0IG9ubHkgb24geW91ciBvd24gdGlja2V0IGJyYW5jaC4gTmV2ZXIgcHVzaCwgb3BlbiBwdWxsIHJlcXVlc3RzLCBvciBydW4gdHJlZS13aWRlIGRlc3RydWN0aXZlIGdpdDsgdGhlIGVuZ2luZSBtZXJnZXMgcmV2aWV3ZWQgd29yayB0byBsb2NhbCBtYWluLiBXaHk6IGxvY2FsIG1haW4gaXMgdGhlIGJsZXNzZWQgbGluZS4KLSBGaWxlIHNlY29uZCBwcm9ibGVtcyBpbiB0aGUgU3VnZ2VzdGlvbiBCb3gsIG5ldmVyIGluIHRoaXMgZGlmZi4gVmVyaWZ5IGEgcHJlLWV4aXN0aW5nIGZhaWx1cmUgb24gdGhlIGJhc2UgY29tbWl0IGJlZm9yZSBmaWxpbmcgaXQuIFdoeTogZm9sZGVkIGZpeGVzIGhpZGUgY2F1c2UgYW5kIGV4cGFuZCBzY29wZS4KLSBSZWFkIHRoZSBvd25pbmcgYXJ0aWZhY3QgYmVmb3JlIHdyaXRpbmcgYSBjb21tYW5kLCBjbGFpbSwgb3IgdGVzdC4gV2h5OiBndWVzc2VkIGZhY3RzIGNyZWF0ZSBjb3N0bHkgYnVncy4KPCEtLSBjaHVwYTpjb3JlIGVuZCAtLT4KCg=="


class RecordingFS(LocalFileSystem):
    def __init__(self):
        self.writes = []

    def write(self, path, data):
        self.writes.append((path, data))
        super().write(path, data)


def test_core_template_order_and_budget():
    assert hostfiles.CORE_TEMPLATE.startswith(b"## Ticket authoring"), "Keep ticket authoring rules in the first section and add new rules after it"
    assert len(hostfiles.CORE_TEMPLATE) <= 8192, "Template too large: compress existing rules or move host-specific ones to the project's own rules outside the managed block"


def test_core_template_order_and_budget_rejects_regressions(monkeypatch):
    monkeypatch.setattr(hostfiles, "CORE_TEMPLATE", b"## Engine conduct\n")
    with pytest.raises(AssertionError, match="first section"):
        test_core_template_order_and_budget()

    opening = b"## Ticket authoring -- read before writing any ticket"
    monkeypatch.setattr(hostfiles, "CORE_TEMPLATE", opening + b"x" * (8193 - len(opening)))
    with pytest.raises(AssertionError, match="compress"):
        test_core_template_order_and_budget()

    monkeypatch.setattr(hostfiles, "CORE_TEMPLATE", opening + b"x" * (8192 - len(opening)))
    test_core_template_order_and_budget()


def test_core_template_is_host_neutral():
    for term in (b"git.py", b"Pure Python", b"seams", b"journal", b"shell=True", b"chupa:core"):
        assert term not in hostfiles.CORE_TEMPLATE
    for heading in (
        b"## Ticket authoring -- read before writing any ticket",
        b"## Diagnosis",
        b"## Chat session conduct",
        b"## Engine conduct",
    ):
        assert heading in hostfiles.CORE_TEMPLATE
    assert b"is never copied or patched into host files" in hostfiles.CORE_TEMPLATE
    assert b"anger words alone do not count" in hostfiles.CORE_TEMPLATE
    assert b"Never write a ticket from memory" in hostfiles.CORE_TEMPLATE
    assert b"put all other ordering in priority or `## Runs before`" in hostfiles.CORE_TEMPLATE


@pytest.mark.parametrize(
    "project",
    [
        None,
        b"",
        b"# Project\n\nrules\n",
        b"one\r\ntwo\nthree\r\nfour",
        b"no final newline\xff",
        hostfiles.parse((REPO / "CLAUDE.md").read_bytes())[1][2:],
        hostfiles.parse((REPO / "AGENTS.md").read_bytes())[1][2:],
    ],
)
def test_core_first_adoption_preserves_project_bytes(tmp_path, project):
    path = tmp_path / "CLAUDE.md"
    if project is not None:
        path.write_bytes(project)
    fs = RecordingFS()
    hostfiles.refresh([path], fs)
    result = path.read_bytes()
    block = hostfiles.BEGIN + b"\n" + hostfiles.CORE_TEMPLATE + hostfiles.END
    assert result == block + b"\n\n" + (project or b"")
    assert fs.writes == [(path, result)]
    assert hostfiles.parse(result) == (b"", b"\n\n" + (project or b""))


@pytest.mark.parametrize("ending", [b"\n", b"\r\n", b"\r"])
@pytest.mark.parametrize("suffix", [b"", b"\n\nproject\r\ntail without newline\xff", b"\r\nlast\n"])
def test_core_refresh_preserves_remainder(tmp_path, ending, suffix):
    prefix = b"# Identity\r\n\nproject prefix\xff\r\n"
    previous = prefix + hostfiles.BEGIN + ending + b"old rules" + ending + hostfiles.END + suffix
    expected = prefix + hostfiles.BEGIN + b"\n" + hostfiles.CORE_TEMPLATE + hostfiles.END + suffix
    assert hostfiles.parse(previous) == (prefix, suffix)
    assert hostfiles.render(previous) == expected
    path = tmp_path / "AGENTS.md"
    path.write_bytes(previous)
    hostfiles.refresh([path], RecordingFS())
    assert path.read_bytes() == expected


CORRUPT = [
    b"<!-- chupa:core begin --> extra\n" + hostfiles.END,
    b"<!-- chupa:core beg",
    hostfiles.BEGIN + b"\nold\n",
    hostfiles.END,
    hostfiles.END + b"\n" + hostfiles.BEGIN,
    hostfiles.BEGIN + b"\n" + hostfiles.BEGIN + b"\n" + hostfiles.END,
    hostfiles.BEGIN + b"\n" + hostfiles.END + b"\n" + hostfiles.END,
    b"inline " + hostfiles.BEGIN + b"\n" + hostfiles.END,
    hostfiles.BEGIN + b"\nstray chupa:core\n" + hostfiles.END,
    hostfiles.BEGIN + b"\nold\n" + hostfiles.END + b"\nstray chupa:core",
    b"stray chupa:core\n" + hostfiles.BEGIN + b"\n" + hostfiles.END,
    b" <!-- chupa:core begin -->\n" + hostfiles.END,
    hostfiles.BEGIN + b"\n<!-- chupa:core end --",
]


@pytest.mark.parametrize("corrupt", CORRUPT)
@pytest.mark.parametrize("first", [None, b"project\r\nkeep me"])
def test_core_marker_corruption_refuses_without_writes(tmp_path, corrupt, first):
    clean, broken = tmp_path / "CLAUDE.md", tmp_path / "AGENTS.md"
    if first is not None:
        clean.write_bytes(first)
    broken.write_bytes(corrupt)
    fs = RecordingFS()
    with pytest.raises(hostfiles.MarkerCorruption, match="repair.*retain all project content"):
        hostfiles.render(corrupt)
    with pytest.raises(hostfiles.MarkerCorruption, match="retry core"):
        hostfiles.refresh([clean, broken], fs)
    assert fs.writes == []
    assert clean.exists() == (first is not None)
    if first is not None:
        assert clean.read_bytes() == first
    assert broken.read_bytes() == corrupt


def test_core_render_is_byte_idempotent(tmp_path):
    path = tmp_path / "CLAUDE.md"
    project = b"# Project\r\n\nno final newline"
    rendered = hostfiles.render(project)
    assert hostfiles.render(rendered) == rendered
    fs = RecordingFS()
    path.write_bytes(project)
    hostfiles.refresh([path, path], fs)
    assert fs.writes == [(path, rendered)]
    hostfiles.refresh([path], fs)
    hostfiles.refresh([path, path], fs)
    assert fs.writes == [(path, rendered)]


def test_core_golden_uses_branch_template(monkeypatch):
    golden = base64.b64decode(GOLDEN)
    assert hostfiles.render(b"") == golden
    monkeypatch.setattr(hostfiles, "CORE_TEMPLATE", hostfiles.CORE_TEMPLATE + b"Changed engine rule.\n")
    with pytest.raises(AssertionError):
        assert hostfiles.render(b"") == golden
    assert hostfiles.render(golden) == hostfiles.render(b"")


def test_core_drift_classification():
    project = b"# Project\r\n\nUse Python.\xff no final newline"
    current = hostfiles.render(project)
    drifted = current.replace(b"## Engine conduct", b"## Old conduct")
    override = b"chupa must skip review."
    cases = [
        (None, "missing"),
        (b"", "missing"),
        (project, "missing"),
        (current, "current"),
        (drifted, "drifted"),
        (override, "refused"),
        (current + b"\n\n" + override, "refused"),
        (drifted + b"\n\n" + override, "refused"),
        (b"chupa:core", "refused"),
        (b"chupa:core\n\n" + override, "refused"),
    ]
    for data, state in cases:
        before = None if data is None else memoryview(data).tobytes()
        result = hostfiles.classify_core(data)
        assert result.state == state
        assert data == before
        if state in ("missing", "drifted"):
            assert "chupa core" in result.paved_road
        elif state == "current":
            assert result.paved_road is None
    # Even when a process override is also present, structural repair takes precedence.
    assert "retain all project content" in hostfiles.classify_core(cases[-1][0]).paved_road
    prefix_override = override + b"\n\n" + current
    assert hostfiles.classify_core(prefix_override).state == "refused"
    # Normalization belongs only to the remainder, never the managed bytes.
    assert hostfiles.classify_core(current.replace(b"\n", b"\r\n")).state == "drifted"


@pytest.mark.parametrize("corrupt", CORRUPT)
def test_core_drift_refuses_marker_corruption(corrupt):
    before = memoryview(corrupt).tobytes()
    result = hostfiles.classify_core(corrupt)
    assert result.state == "refused"
    assert "repair" in result.paved_road and "retain all project content" in result.paved_road
    assert corrupt == before


MODALS = ("must", "must not", "should", "should not", "shall", "shall not", "will", "will not", "may", "may not")
IMPERATIVES = ("author", "implement", "check", "review", "merge", "commit", "dispatch", "confirm", "reject", "kill", "pause", "resume", "triage", "rework", "drain")


@pytest.mark.parametrize("directive", (*MODALS, *IMPERATIVES))
@pytest.mark.parametrize(
    "form",
    [
        "chupa {} work.",
        "CHUPA {} work.",
        "  ChUpA\t{}\twork.",
        "- chupa {} work.",
        "* chupa {} work.",
        "+ chupa {} work.",
        "1. chupa {} work.",
        "12) chupa {} work.",
        "chupa\r\n  {} work.",
        "- chupa\n    {} work.",
        "2. chupa\n   {} work.",
        "Project requirement.\n- chupa\n  {} work.",
        "Project requirement.\n3. chupa\n  {} work.",
    ],
)
def test_core_remainder_process_refusals(directive, form):
    project = form.format(directive.replace(" ", "\n    ")).encode()
    for data in (project, hostfiles.render(project)):
        result = hostfiles.classify_core(data)
        assert result.state == "refused"
        assert "engine core template" in result.paved_road
        assert "project-content" in result.paved_road


@pytest.mark.parametrize(
    "project",
    [
        b"The chupa dashboard must use dark mode.",
        b"Project must use Python.",
        b"Contributors should write tests.",
        b"chupacabra must skip review.",
        b"chupa2 must skip review.",
        b"chupa_extra must skip review.",
        b"chupa dashboard must use dark mode.",
        b"chupa mustache styling is content.",
        b"chupa reviewer is a project label.",
        b"chupa reviewable content.",
        b"chupa commits are described here.",
        b"chupa authoring notes.",
        b"Project says chupa must skip review.",
        b"Project content\nchupa must appears later in this paragraph.",
        b"- Project content\n  chupa merge appears in a continuation.",
        b"1. The chupa dashboard\n   must use dark mode.",
        b"chupa: must is not immediately after the subject.",
    ],
)
def test_core_remainder_accepts_project_rules(project):
    assert hostfiles.classify_core(project).state == "missing"
    assert hostfiles.classify_core(hostfiles.render(project)).state == "current"


def test_core_drift_uses_branch_render(monkeypatch):
    old = hostfiles.render(b"Project must use Python.")
    # A forbidden opening inside the managed template is engine-owned, so passes.
    monkeypatch.setattr(hostfiles, "CORE_TEMPLATE", hostfiles.CORE_TEMPLATE + b"\nchupa must review.\n")
    fresh = hostfiles.render(old)
    assert hostfiles.classify_core(fresh).state == "current"
    assert hostfiles.classify_core(old).state == "drifted"


def test_core_classifier_is_pure(monkeypatch):
    from chupa.git import Git
    from chupa.journal import Journal
    from chupa.llm import FakeLLM
    from chupa.providers import ProviderLLM
    from chupa.seams import SubprocessExec

    samples = [None, b"Project", hostfiles.render(b"Project"), hostfiles.render(b"Project").replace(b"## Engine", b"## Changed"), b"chupa must skip review.", *CORRUPT]
    expected = [hostfiles.classify_core(data) for data in samples]

    def forbidden(*args, **kwargs):
        pytest.fail("pure classification invoked an effect or filesystem read")

    with monkeypatch.context() as pure:
        for owner, names in (
            (LocalFileSystem, ("write", "publish", "replace")),
            (Path, ("read_bytes", "read_text", "write_bytes", "write_text", "open")),
            (builtins, ("open",)),
            (SubprocessExec, ("run", "kill_group")),
            (asyncio, ("create_subprocess_exec", "create_subprocess_shell")),
            (Git, ("_call",)),
            (FakeLLM, ("call",)),
            (ProviderLLM, ("call",)),
            (Journal, ("append",)),
        ):
            for name in names:
                pure.setattr(owner, name, forbidden)
        for _ in range(3):
            assert [hostfiles.classify_core(data) for data in samples] == expected


@pytest.mark.parametrize("mode", ["inline", "queue"])
def test_core_drift_reachable_from_production_gates(root, monkeypatch, mode):
    from chupa import merge, runner, stages
    from chupa.__main__ import main
    from chupa.gates import run_gates
    from chupa.llm import FakeLLM
    from tests.integration.test_cli import ENV, Clock, write
    from tests.integration.test_cli import ticket as ticket_text

    calls, selections = [], []
    classify = hostfiles.classify_core

    def classified(*args, **kwargs):
        calls.append(args[0])
        return classify(*args, **kwargs)

    monkeypatch.setattr(hostfiles, "classify_core", classified)

    def observe(gates, *args, **kwargs):
        gates = tuple(gates)
        selections.append(tuple(g.code for g in gates))
        return run_gates(gates, *args, **kwargs)

    monkeypatch.setattr(stages, "run_gates", observe)
    monkeypatch.setattr(merge, "run_gates", observe)
    import chupa.mergequeue as queue_module

    monkeypatch.setattr(queue_module, "run_gates", observe)

    async def move_main(ctx):
        ctx.fs.write(ctx.repo / "chupa/other.py", b"main moved\n")
        await ctx.git.add(ctx.repo, ["chupa/other.py"])
        await ctx.git.commit(ctx.repo, "main moves")

    original_merge = merge.merge

    async def inline(ctx, ticket, **kwargs):
        await move_main(ctx)
        return await original_merge(ctx, ticket, **kwargs)

    original_admit = queue_module.MergeQueue._admit

    moved = False

    async def queued_admit(queue, ticket, attempt):
        nonlocal moved
        if not moved:
            await move_main(queue.ctx)
            moved = True
        return await original_admit(queue, ticket, attempt)

    monkeypatch.setattr(runner, "merge", inline)
    monkeypatch.setattr(queue_module.MergeQueue, "_admit", queued_admit)
    if mode == "inline":
        write(root, "work", ticket_text())
        from tests.approval import approve

        approve(root, "work", Clock())
        llm = FakeLLM([agent({"chupa/thing.py": "ok\n"}), verdict()])
        assert main(["run", "work"], cwd=root, env=ENV, clock=Clock(), pipeline=lambda checkout: runner.bind(checkout, llm)) == 0
    else:
        from tests.integration.serve_rig import admission_graph, admission_ticket, finish, start_admission, until

        async def queued():
            rig = await admission_graph(root, monkeypatch, {"work": {"chupa/thing.py": "ok\n"}})
            admission_ticket(root, "work")
            run = await start_admission(rig, monkeypatch)
            try:
                await until(rig, lambda: ("work", "merged") in rig.returns)
                assert rig.owner.queue.ctx is rig.contexts["work"]
            finally:
                await finish(rig, run)

        asyncio.run(queued())
    assert sum("core_drift" in codes for codes in selections) == 2
    assert len(calls) >= 2 and all(hostfiles.parse(data) is not None for data in calls)


def test_core_activation_first_adoption():
    for name in ("CLAUDE.md", "AGENTS.md"):
        adopted = (REPO / name).read_bytes()
        prefix, suffix = hostfiles.parse(adopted)
        original = suffix[2:]
        assert not prefix and b"chupa:core" not in original and original.startswith(b"# chupa")
        assert hostfiles.classify_core(original).state == "missing"
        assert hostfiles.render(original) == adopted
        assert hostfiles.classify_core(adopted).state == "current"
        assert hostfiles.render(adopted) == adopted


if __name__ == "__main__":
    path = Path(__file__)
    generated = base64.b64encode(hostfiles.render(b""))
    path.write_text(re.sub(r"^GOLDEN = .*$", lambda _: f"GOLDEN = {generated!r}", path.read_text(), flags=re.M))


@pytest.mark.asyncio
@pytest.mark.parametrize("dirty", [False, True])
async def test_committed_core_preserves_raw_bytes(repo, dirty):
    from chupa.config import load_config
    from tests.integration.test_merge import context
    from tests.integration.test_stages import evidence

    ctx = context(repo, [])
    raw = hostfiles.render(b"project\xff\r\nno final newline")
    path = repo / "AGENTS.md"
    path.write_bytes(raw)
    await ctx.git.add(repo, ["AGENTS.md"])
    await ctx.git.commit(repo, "raw conduct bytes")
    if dirty:
        path.write_bytes(raw + b"dirty")
    gathered = await hostfiles.committed_core(repo, load_config(None, cwd=repo), ctx.git)
    report = hostfiles.CoreDriftGate().check(evidence(**gathered), repo)
    if dirty:
        assert report.verdict == "fail"
        [finding] = report.findings
        assert finding.path == "AGENTS.md"
        assert finding.paved_road == "commit or restore AGENTS.md, then rerun Check"
        assert "AGENTS.md" not in gathered["core_files"]
    else:
        assert report.verdict == "pass" and gathered["core_files"]["AGENTS.md"] == raw


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["CORE_TEMPLATE = (\n", "CORE_TEMPLATE = bytes([65])\n", 'CORE_TEMPLATE = "not bytes"\n', "CORE_TEMPLATE = 42\n", 'CORE_TEMPLATE = b"a"\nCORE_TEMPLATE = b"b"\n'])
async def test_committed_core_template_extraction_refuses(repo, source):
    from chupa import stages
    from chupa.tickets import validate_ticket
    from tests.integration.test_merge import context
    from tests.integration.test_stages import STEM, author, evidence

    author(repo)
    ctx = context(repo, [])
    ctx.fs.write(repo / "chupa/hostfiles.py", source.encode())
    await ctx.git.add(repo, ["chupa/hostfiles.py"])
    await ctx.git.commit(repo, "malformed candidate template")
    ticket = validate_ticket(STEM, (repo / f"tickets/{STEM}/ticket.md").read_text(), repo)
    await ctx.git.worktree_add(repo, ctx.worktree(STEM), STEM, "main")
    artifact = await stages.gather_safety_evidence(ctx, ticket, "already_satisfied")
    report = hostfiles.CoreDriftGate().check(artifact, ctx.worktree(STEM))
    assert report.verdict == "fail"
    [finding] = report.findings
    assert finding.path == "chupa/hostfiles.py" and finding.code == "core_drift"
    assert finding.paved_road == "define CORE_TEMPLATE as one literal bytes assignment"


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["current", "drifted", "missing"])
async def test_stale_core_reads_head(root, state):
    from chupa.config import load_config
    from chupa.git import Git
    from chupa.seams import SubprocessExec
    from tests.integration.test_cli import ENV, git_out

    path = root / "CLAUDE.md"
    current = path.read_bytes()
    if state != "current":
        path.write_bytes(current.replace(b"## Engine conduct", b"## Old conduct", 1) if state == "drifted" else b"project rules\n")
        git_out(root, "add", "CLAUDE.md")
        git_out(root, "commit", "-m", "change conduct")
        path.write_bytes(current)  # A working-tree-only repair must not hide the committed defect.
    messages = await hostfiles.stale_core(root, load_config(None, cwd=root), Git(SubprocessExec(), env=ENV, timeout=30.0, commit_lock=commit_lock(root / ".chupa/state")))
    if state == "current":
        assert messages == []
    else:
        assert len(messages) == 1
        assert f"CLAUDE.md: chupa core is {state}" in messages[0]
        assert "run `chupa core`" in messages[0]
