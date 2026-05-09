const APPS = [
  { id: "war-markets", label: "Money + War", href: "https://www.money4war.com/" },
  { id: "tech-spend", label: "Tech Spend", href: "https://www.money4war.com/tech-spend/" },
  { id: "options", label: "Options", href: "/" },
];

const CURRENT = "options";

export default function AppSwitcher() {
  return (
    <nav
      aria-label="Sibling apps"
      className="flex items-center gap-1 rounded-full border border-slate-700/60 bg-slate-900/60 backdrop-blur px-1 py-1"
    >
      {APPS.map((app) => {
        const active = app.id === CURRENT;
        return (
          <a
            key={app.id}
            href={app.href}
            aria-current={active ? "page" : undefined}
            className={
              "px-3 py-1 text-xs font-medium rounded-full transition-colors " +
              (active
                ? "bg-indigo-500/20 text-indigo-300 ring-1 ring-indigo-500/40"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40")
            }
          >
            {app.label}
          </a>
        );
      })}
    </nav>
  );
}
