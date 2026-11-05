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
   - the web apps: vectors / light / layout / one.horix.live (horix.live and horix.si by
     running "Deploy HORIX" (deploy-sg-ps.yml) from the Actions tab: it no longer runs on every
     push, to save Actions minutes);
   - the desktop releases: Vectors, Light and Layout (desktop-horix-family.yml), and HORIX One
     (horix-one.yml), on their VERSION changes; HORIX by running "Desktop HORIX"
     (desktop-sg-ps.yml) from the Actions tab;
   - the Mac downloads on horix.si/mac and the Launcher feed, after the releases.
   Merge with a commit message of your own (the PR title): a squash merge otherwise lists every
   commit's message, and a "[skip ci]" in any of them stops every workflow the merge should run.
3. Don't merge anything else while HORIX One's release run is going: a newer push to the branch
   cancels it (its concurrency group), and the new run would not release.
4. GitHub runs only two macOS jobs at a time for this account, and a job that waits about 15
   minutes for a Mac is cancelled. If one is, re-run its failed jobs once a Mac is free (a re-run
   adds its files to the release it already made).
5. Check every site and download live, then send the week's summary.

## Urgent fixes

A fix for something broken for users ships right away, outside the Thursday update.

## Languages: Arabic and English only

HORIX is for Arabic and English speakers (Saber Group's decision of 2026-11-05). When bringing in
a new upstream (ArtCraft) version:

- Don't spend work on what serves only other languages: interface translations other than
  Arabic and English, hyphenation patterns, East Asian type settings, and the like. Take
  whatever helps Arabic and English users (tools, file formats, speed, right-to-left text).
- The interface language menu in every app offers English and العربية only. Keep upstream's
  other translations in the code (hidden), so each upgrade doesn't fight upstream over them.
