# Windows installation of PSLinkedIn v0.1.0

The GitHub workflow builds libraries only. Keep your decrypted LinkedIn IPA, Apple ID, passwords, signing certificate and provisioning profile on your Windows PC. Never attach these to an issue or upload them as Actions artifacts or secrets. Do not run dev.sh in Actions: it combines building with macOS-only injection, signing and installation.

## Download the build

Open this repository's Actions tab, select a successful **Build arm64 dylibs** run, then download and extract **PSLinkedIn-v0.1.0-arm64**. GitHub requires login to download Actions artifacts. The ZIP contains:

- PSLinkedIn.dylib
- FLEXing.dylib
- libFLEX.dylib
- BUILD-INFO.txt, LICENSE and NOTICE

Use all three libraries from the same run, keeping their filenames. BUILD-INFO.txt records source, toolchain and SDK revisions, Xcode version and SHA-256 checksums. Check the run is successful; a workflow file alone is not evidence of a working build.

## Inject, sign and install locally

1. Install the current Windows release from [Sideloadly's official site](https://sideloadly.io/). Follow its Windows prerequisites: the web versions of iTunes and iCloud linked there, rather than the Microsoft Store versions.
2. Keep your own legally obtained **decrypted** LinkedIn IPA in a private folder outside your repository. Upstream tested **LinkedIn 9.1.555**; start with that version for the best chance of matching its private classes and tab IDs. An encrypted App Store IPA is not a compatible input. This workflow does not obtain or decrypt an IPA.
3. Connect the iPhone 15 Pro by USB, unlock it and trust the PC. Confirm Sideloadly sees the phone.
4. Load the IPA into Sideloadly. Open Advanced Options, enable **Inject dylibs/frameworks**, and use its add-file control to select **PSLinkedIn.dylib**, **FLEXing.dylib** and **libFLEX.dylib**. Enable **Cydia Substrate** support where offered: PSLinkedIn uses the default Logos substrate hooks. FLEXing uses the internal generator. UI wording may differ between releases.
5. Set a distinct bundle ID, such as **com.ninomenriquez.pslinkedin**, so this installs alongside official LinkedIn. Use the same bundle ID and Apple ID for subsequent refreshes.
6. Remove app extensions/PlugIns using Sideloadly's extension removal option, matching upstream's installation approach. Do not enable additional generic sideload fix patches if optional: PSLinkedIn already includes its own app-group and keychain fixes. Leave the minimum OS version alone.
7. Select Apple ID signing/install mode, enter your Apple ID and any authentication prompts **only in the local Sideloadly app**, then start. Sideloadly handles provisioning and signing; this route does not require exporting a .p12 or provisioning profile to GitHub.
8. On the iPhone, enable **Settings > Privacy & Security > Developer Mode** when prompted, including the restart/confirmation. Trust the developer under **Settings > General > VPN & Device Management** if needed, then open PSLinkedIn.

Sideloadly documents Windows support, multiple-library injection, Cydia Substrate support, bundle ID changes and extension removal. Its compatibility rewriting is not a guarantee that every tweak will run. This is the simplest supported Windows path, but device behavior must still be checked below. A successful CI build cannot verify installation or LinkedIn login.

With a free Apple account, the app generally needs re-signing every seven days. Sideloadly's refresh daemon can handle this when the PC and device can connect. Follow the [official FAQ](https://sideloadly.io/faq) for setup and account limits.

## Verify the initial installation

Record the iOS version, LinkedIn version and Actions run used. On a fresh install:

- The app launches and opens on My Network.
- Home and Post are absent from the bottom tabs.
- A full-screen vertical video feed cannot be opened.
- My Network loads profiles/connections; Jobs loads and opens job details.
- Messages open and a test message sends/receives.
- Search returns results and opens a profile; Notifications and profile still work.
- After closing/reopening, login and the tab behavior persist.
- Hold four fingers for one second to open settings. Hide Home feed, Block video feed and Hide Post are enabled. Existing settings can be restored from keychain, so check these if this is a reinstall.

These checks require your phone and account. They are not performed by GitHub Actions. App extensions (share sheet/widgets/rich notifications) are intentionally removed as in upstream.

## Troubleshooting

- **No device:** check Apple's Windows drivers, USB trust and the official Sideloadly FAQ.
- **Installation/signing failure:** use the Sideloadly log to distinguish provisioning/account limits from injection failures. Keep credentials and device/account identifiers private.
- **Crash at launch:** confirm the IPA is decrypted, all three libraries came from one arm64 artifact, Substrate support is enabled, extensions were removed and no extra fix patches were selected. Capture the device crash log locally; a missing-library/dyld error needs its exact dependency path.
- **Login fails:** compare LinkedIn version with 9.1.555 and inspect local signing/keychain errors. Preserve upstream's sideload fixes; do not add broad entitlement workarounds. Upstream's macOS dev.sh filters entitlements, while Sideloadly manages them independently.
- **Feed still visible:** confirm the version matches, all three settings are enabled, then force-quit/relaunch. LinkedIn can change private class names or server-driven UI; compiling does not establish compatibility with newer LinkedIn versions.
- **Update fails:** first retry with the same Apple ID and bundle ID. Removing/reinstalling may require LinkedIn login again. Do not delete an installation containing needed local data without backing it up.

## Build details

The Makefile targets arm64 and SDK 16.2. The workflow uses pinned Theos, the exact upstream Logos compatibility revision **a62370066a97e36d59b200a9fa10c5091f5e8972**, and the iOS 16.2 SDK from the repository linked by upstream. Recursive checkout preserves the FLEXing, FLEX and Reflex gitlink revisions; fishhook is vendored in the source.

The main tweak and FLEXing aggregate are built explicitly using the actual **modules/FLEXing** casing. This avoids upstream's lower-case **modules/flexing** subproject path and ensures both dependency libraries exist. All libraries use arm64, SDK 16.2 and deployment target 15.0. No feature source is modified. The macOS/Xcode runner receives updates; this is a pinned-source build recipe, not a claim of byte-identical outputs across runner updates.

Upstream references: [README](https://github.com/pstepanovum/PSLinkedIn#readme), [dev.sh](https://github.com/pstepanovum/PSLinkedIn/blob/main/dev.sh), [Makefile](https://github.com/pstepanovum/PSLinkedIn/blob/main/Makefile).
