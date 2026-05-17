# One-time setup (repo owner)

Do these once so friends can pull images and use the download page.

## 1. GitHub Pages (download site)

**Settings → Pages → Build and deployment → Source:** `GitHub Actions`

After the next push to `main`, the site will be at:

**https://tanvir-commits.github.io/AIBox/**

Set **Settings → General → Website** to that URL (shows on the repo home).

## 2. Public container packages (fixes `docker pull` / exe pull)

Public **repo** ≠ public **packages**. For each package:

1. Open https://github.com/users/tanvir-commits/packages
2. Click **`aibox-backend`** → **Package settings** → **Change visibility** → **Public**
3. Repeat for **`aibox-web`**

CI also tries to set visibility on each publish; confirm in the UI if pulls still fail.

## 3. Latest release for friends

https://github.com/tanvir-commits/AIBox/releases/latest

Asset: `privateai-box-v0.3.1-mvp-windows.zip` (or newer tag).
