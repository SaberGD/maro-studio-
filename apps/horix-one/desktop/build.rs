//! The Windows exe's icon and version. HORIX Launcher checks the exe's ProductVersion against the
//! release it installed (HORIX_VERSION, set by package.sh), so it must be the release's.
fn main() {
    println!("cargo:rerun-if-env-changed=HORIX_VERSION");
    println!("cargo:rerun-if-changed=../assets/app-icon/icon.ico");
    if std::env::var("CARGO_CFG_TARGET_OS").as_deref() != Ok("windows") {
        return;
    }
    let mut res = winresource::WindowsResource::new();
    res.set_icon("../assets/app-icon/icon.ico");
    res.set("ProductName", "HORIX One").set("FileDescription", "HORIX One").set("CompanyName", "Saber Group");
    if let Ok(v) = std::env::var("HORIX_VERSION") {
        res.set("ProductVersion", &v).set("FileVersion", &v);
    }
    if let Err(e) = res.compile() {
        println!("cargo:warning=no Windows resources: {e}");
    }
}
