# GitHub Publish

`github-publish` is a repository-specific publication guard, not a Git tutorial or generic delivery workflow.

Codex performs ordinary Git/GitHub operations natively. This capability adds deterministic checks for:

- non-default-branch publication;
- repository-local author/committer identity;
- configured GitHub account;
- Conventional Commits 1.0.0;
- GitHub repository description;
- upstream/conflict/push safety;
- explicit staging boundaries;
- mandatory pull-request publication.

Runtime contract: [`skills/github-publish/SKILL.md`](../../../skills/github-publish/SKILL.md).

Managed scripts remain under `skills/github-publish/scripts/`. They are the reason this capability remains a Skill: they turn repository publication policy into deterministic checks rather than model instructions.
