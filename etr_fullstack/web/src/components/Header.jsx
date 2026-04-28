const isteLogo = "/iste logo.jpg";
const triveniLogo = "/trevini logo.jpg";

function Header() {
  return (
    <header className="relative mb-10 border-b border-zinc-800 px-6 py-8">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4">
        <img
          src={isteLogo}
          alt="ISTE logo"
          className="h-12 w-12 rounded-full border border-amber/70 bg-black/60 object-cover p-0.5 shadow-[0_0_18px_rgba(255,191,0,0.55)]"
        />

        <div className="text-center">
          <p className="mb-3 text-xs tracking-[0.45em] text-zinc-400">ISTE BITS presents TRIVENI'26</p>
          <h1 className="text-5xl font-bold uppercase tracking-[0.25em] text-steel md:text-7xl">
            Escape The Room
          </h1>
          <p className="mt-3 text-xs tracking-[0.3em] text-amber">DEEP SPACE PROTOCOL | ENDURANCE STATION</p>
        </div>

        <img
          src={triveniLogo}
          alt="Triveni eagle logo"
          className="h-12 w-12 rounded-full border border-amber/70 bg-black/60 object-cover p-0.5 shadow-[0_0_18px_rgba(255,191,0,0.55)]"
        />
      </div>
    </header>
  );
}

export default Header;
