from .checks import has_required_label, is_author_allowed
from .github_api import GithubClient
from .settings import Settings


def main() -> None:
    cfg = Settings.from_env()

    approved = skipped = 0

    with GithubClient(cfg.token) as client:
        me = client.get_authenticated_user()
        print(f"Authenticated as: {me}")
        print(f"Owners     : {cfg.owners}")
        print(f"Authors    : {cfg.allowed_authors}")
        print(f"Label      : {cfg.required_label}")
        print(f"Dry run    : {cfg.dry_run}\n")

        for owner in cfg.owners:
            print(f"=== {owner} ===")
            repos = client.list_repos(owner)
            print(f"  {len(repos)} active repos")

            for repo in repos:
                prs = client.list_open_prs(repo)
                if not prs:
                    continue

                for pr in prs:
                    tag = f"{repo.full_name}#{pr.number}"
                    author = pr.user.login
                    labels = [lb.name for lb in pr.labels]

                    if not is_author_allowed(author, cfg.allowed_authors):
                        print(f"  SKIP    {tag} — author '{author}' not in allowed list")
                        skipped += 1
                        continue

                    if not has_required_label(labels, cfg.required_label):
                        print(f"  SKIP    {tag} — label '{cfg.required_label}' not present")
                        skipped += 1
                        continue

                    if not client.is_ci_passing(repo, pr.head.sha):
                        print(f"  SKIP    {tag} — CI not passing")
                        skipped += 1
                        continue

                    if client.is_already_approved(pr, me):
                        print(f"  SKIP    {tag} — already approved by {me}")
                        skipped += 1
                        continue

                    if cfg.dry_run:
                        print(f"  DRY-RUN  {tag}  {pr.html_url}")
                    else:
                        client.approve_pr(
                            pr=pr,
                            body=(
                                f"Auto-approved: authored by `{author}`, "
                                f"label `{cfg.required_label}` present, CI passing."
                            ),
                        )
                        print(f"  APPROVED {tag}  {pr.html_url}")
                    approved += 1

    print(f"\nDone — approved: {approved}  skipped: {skipped}")
