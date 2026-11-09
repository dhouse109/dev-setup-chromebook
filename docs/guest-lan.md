# Local NT/2000 guest link (v101)

`winnt40 lan [status|on|off]` and `win2000 lan [status|on|off]` manage one second
PCnet adapter per guest. The default is off. The link uses reciprocal loopback UDP
endpoints on this Linux host; remote peers, multicast, TAP and bridging are deferred.
No command boots a guest or changes Windows IP, WINS, domain or driver settings.

| Guest | Host UDP bind | Host UDP peer | Second-adapter MAC | Existing guest IP |
|---|---|---|---|---|
| NT 4.0 | 127.0.0.1:10001 | 127.0.0.1:10002 | 52:54:00:50:00:10 | 192.168.50.10 |
| Windows 2000 | 127.0.0.1:10002 | 127.0.0.1:10001 | 52:54:00:50:00:20 | 192.168.50.20 |

The guest second adapters retain mask 255.255.255.0, no gateway and WINS
192.168.50.10. Preserve the already-working HADAMIN domain relationship. The first
user-mode adapter keeps its internet route; host UDP ports are not guest IP ports.

## Config and commands

Settings stay in `~/winnt40/config` and `~/win2000/config`, alongside CPU/audio and
EXTRA_ARGS. `LAN_ENABLED` is 0 or 1; `LAN_LOCAL_PORT` and `LAN_PEER_PORT` are distinct
ports from 1024 through 65535; `LAN_MAC` is a nonzero unicast MAC. The two files must
have reciprocal ports and distinct MACs. Both host endpoints and the PCnet model
are fixed by the helper. Existing configs gain missing keys only on an explicit
change; an already-off legacy config is left alone.

`lan` without another argument means `lan status`. Status reads literals without
sourcing config and creates no workspace, state, log or socket. Complex config is
reported for manual review. Status never pings, probes a port or launches an engine.
On/off require an existing regular config and a stopped guest. Edits preserve mode,
line endings, comments, unrelated assignments and the old defaults-review markers.
Symlinks, duplicate/unknown LAN keys and ambiguous shell constructs are refused.

Enabling checks the peer config and local UDP port. An occupied port is reported;
the helper never kills its owner or chooses another port. Launch validates the
effective settings again before opening guest disks. The link applies to boot,
run and explicitly requested setup; setup still withholds the exchange disk.

## Adopt an existing handwritten second adapter

1. While the old link is still available, record both adapters' model, MAC,
   guest-visible PCI bus/slot/function, IP, mask, gateway and WINS. Record the full
   handwritten launch/device argument sequence. Then shut down both guests and
   keep recoverable config/disk backups. Save the notes and config copies under
   the bundle's `assets/logs/guest-lan/`. Do not guess a slot from this document.
2. Run `winnt40 lan status` and `win2000 lan status`. Review both configs. If
   EXTRA_ARGS contains the old `-nic socket` or other networking, `lan on` refuses
   it. Remove only that known link stanza yourself after recording it; the helper
   never deletes owner arguments. If the old MAC/ports differ from the table, set
   the matching LAN keys in both configs before enabling. Keep the old identities.
3. For the proven suffix layout, the old socket NIC was the last device argument
   in EXTRA_ARGS, after the helper's user NIC, USB and audio. The managed NIC is
   emitted at that same position, after the remaining preceding EXTRA_ARGS. An
   empty or non-device EXTRA_ARGS therefore preserves that layout.
4. Custom device layouts require manual review. An unpinned extra `-device` is
   refused. Use `LAN_PCI_ADDR` and optional `LAN_PCI_BUS` only for the **recorded
   original** NIC location, with recorded explicit addresses for all other custom
   PCI devices in EXTRA_ARGS. The helper emits socket `-netdev` plus
   `-device pcnet,...,addr=...` in this form. It rejects slot collisions and unknown
   placement. Explicit pins preserve effective placement when the old NIC was
   before another custom device. If the original placement is unknown, stop and
   restore the old config; do not pick an unused slot.
5. With both guests stopped, run `winnt40 lan on` and `win2000 lan on`, then their
   status commands. The owner launches the guests explicitly. **Neither guest
   may detect new hardware.** Both must retain the original second adapter's
   static IP/WINS without re-entry. Check bidirectional ping, the existing domain
   relationship and first-adapter internet. Record results under assets.
6. Shut down both guests before `lan off`. The second adapter disappears at the
   next owner-started boot. Re-enabling must recover the same identity/settings.
   New hardware or lost settings is a regression: stop, restore the original
   config and investigate placement. Driver rebinding is not acceptance.

No guest hand check has been claimed by the isolated argv fixtures. Begin with
NT's current 128 MB and Windows 2000's 256 MB allocations. Cross-laptop transport,
including the Tailscale 1280 MTU/encapsulated-frame risk, is companion work package
F6. Delphi application, DCOM/database configuration and service-pack installation
remain owner-controlled follow-up work.
