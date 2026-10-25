# HORIX family releases: every Thursday

Changes to the HORIX family (HORIX, HORIX Vectors, HORIX Light, HORIX Layout, HORIX One, the
Launcher, horix.si) ship together once a week, on Thursday, as Saber Group decided on 2026-10-25.

## During the week

- All the week's work goes into one pull request against `claude/nice-shannon-7w6xo5`, the
  "weekly update". Nothing reaches users until it is merged.
- HORIX One needs no separate work: it is built from the same sources and patches as HORIX,
  HORIX Vectors and HORIX Layout (apps/horix-one/native/prepare.sh, apps/horix-one/build.sh), so
  every change to those apps is in HORIX One's next build.
- Each change is built and tried (CI, plus screenshots for anything visible) before Thursday.

## On Thursday

1. Bump the VERSION of every app the week changed (HORIX One whenever HORIX, Vectors or Layout
   changed; the Launcher when its catalog changed).
2. Wait for CI to be green, then merge. That one merge publishes everything:
   - the web apps: horix.live, vectors / light / layout / one.horix.live, and horix.si;
   - the desktop releases: Vectors, Light and Layout (desktop-horix-family.yml), and HORIX One
     (horix-one.yml), on their VERSION changes; HORIX by running "Desktop HORIX"
     (desktop-sg-ps.yml) from the Actions tab;
   - the Mac downloads on horix.si/mac and the Launcher feed, after the releases.
3. Don't merge anything else while HORIX One's release run is going: a newer push to the branch
   cancels it (its concurrency group), and the new run would not release.
4. Check every site and download live, then send the week's summary.

## Urgent fixes

A fix for something broken for users ships right away, outside the Thursday update.
