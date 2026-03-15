"""World registry models and loaders.

The registry tracks all federation nodes: cities (runtime environments)
and agents (autonomous operators). Both are peers in the federation.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import load_yaml


@dataclass(frozen=True, slots=True)
class CityRecord:
    city_id: str
    repo: str
    status: str
    registered_at: str
    trust_level: str
    federation_endpoint: str
    projection_source: str
    last_heartbeat: str | None
    capabilities: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "city_id": self.city_id,
            "repo": self.repo,
            "status": self.status,
            "registered_at": self.registered_at,
            "trust_level": self.trust_level,
            "federation_endpoint": self.federation_endpoint,
            "projection_source": self.projection_source,
            "last_heartbeat": self.last_heartbeat,
            "capabilities": list(self.capabilities),
        }


@dataclass(frozen=True, slots=True)
class AgentRecord:
    """A registered federation agent (operator, substrate, control plane, etc.)."""

    agent_id: str
    repo: str
    status: str
    registered_at: str
    trust_level: str
    owner_boundary: str
    capabilities: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "agent_id": self.agent_id,
            "repo": self.repo,
            "status": self.status,
            "registered_at": self.registered_at,
            "trust_level": self.trust_level,
            "owner_boundary": self.owner_boundary,
            "capabilities": list(self.capabilities),
        }


@dataclass(frozen=True, slots=True)
class WorldRegistry:
    world_id: str
    origin_id: str
    steward_substrate: str
    public_projection: str
    cities: tuple[CityRecord, ...]
    agents: tuple[AgentRecord, ...]

    def city_by_id(self, city_id: str) -> CityRecord:
        for city in self.cities:
            if city.city_id == city_id:
                return city
        raise KeyError(city_id)

    def agent_by_id(self, agent_id: str) -> AgentRecord:
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        raise KeyError(agent_id)

    @property
    def all_repos(self) -> list[str]:
        """All repos in the federation (cities + agents, deduplicated)."""
        repos: set[str] = set()
        for city in self.cities:
            repos.add(city.repo)
        for agent in self.agents:
            repos.add(agent.repo)
        return sorted(repos)


def load_world_registry(*, base_path=None) -> WorldRegistry:
    payload = load_yaml("config/world_registry.yaml", base_path=base_path)
    world = payload.get("world") or {}
    cities_payload = payload.get("cities") or []
    agents_payload = payload.get("agents") or []
    return WorldRegistry(
        world_id=str(world.get("world_id") or "").strip(),
        origin_id=str(world.get("origin_id") or "").strip(),
        steward_substrate=str(world.get("steward_substrate") or "").strip(),
        public_projection=str(world.get("public_projection") or "").strip(),
        cities=tuple(
            CityRecord(
                city_id=str(item.get("city_id") or "").strip(),
                repo=str(item.get("repo") or "").strip(),
                status=str(item.get("status") or "").strip(),
                registered_at=str(item.get("registered_at") or "").strip(),
                trust_level=str(item.get("trust_level") or "").strip(),
                federation_endpoint=str(item.get("federation_endpoint") or "").strip(),
                projection_source=str(item.get("projection_source") or "").strip(),
                last_heartbeat=item.get("last_heartbeat"),
                capabilities=tuple(item.get("capabilities") or []),
            )
            for item in cities_payload
        ),
        agents=tuple(
            AgentRecord(
                agent_id=str(item.get("agent_id") or "").strip(),
                repo=str(item.get("repo") or "").strip(),
                status=str(item.get("status") or "").strip(),
                registered_at=str(item.get("registered_at") or "").strip(),
                trust_level=str(item.get("trust_level") or "").strip(),
                owner_boundary=str(item.get("owner_boundary") or "").strip(),
                capabilities=tuple(item.get("capabilities") or []),
            )
            for item in agents_payload
        ),
    )
