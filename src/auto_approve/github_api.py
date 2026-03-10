from github import Auth, Github
from github.PullRequest import PullRequest
from github.Repository import Repository

PASSING_CONCLUSIONS = {"success", "neutral", "skipped"}


class GithubClient:
    def __init__(self, token: str) -> None:
        self._gh = Github(auth=Auth.Token(token))

    def get_authenticated_user(self) -> str:
        return self._gh.get_user().login

    def list_repos(self, owner: str) -> list[Repository]:
        try:
            return [r for r in self._gh.get_organization(owner).get_repos() if not r.archived]
        except Exception:
            return [r for r in self._gh.get_user(owner).get_repos() if not r.archived]

    def list_open_prs(self, repo: Repository) -> list[PullRequest]:
        return list(repo.get_pulls(state="open"))

    def is_ci_passing(self, repo: Repository, sha: str) -> bool:
        runs = list(repo.get_commit(sha).get_check_runs())
        if not runs:
            return True
        return all(
            r.status == "completed" and r.conclusion in PASSING_CONCLUSIONS
            for r in runs
        )

    def is_already_approved(self, pr: PullRequest, reviewer: str) -> bool:
        return any(
            r.user.login == reviewer and r.state == "APPROVED"
            for r in pr.get_reviews()
        )

    def approve_pr(self, pr: PullRequest, body: str) -> None:
        pr.create_review(event="APPROVE", body=body)

    def close(self) -> None:
        self._gh.close()

    def __enter__(self) -> "GithubClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
