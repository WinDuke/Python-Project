"""A* pathfinding implementation."""

import heapq
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


@dataclass(order=True)
class PriorityNode:
    """Node for priority queue."""
    priority: float
    position: tuple[int, int] = field(compare=False)


class PathFinder:
    """A* pathfinding implementation for grid-based movement."""

    def __init__(self, is_blocked: Callable[[int, int], bool]):
        """
        Initialize pathfinder.
        
        Args:
            is_blocked: Function that returns True if a tile is blocked.
        """
        self._is_blocked = is_blocked

    def find_path(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        allow_diagonal: bool = True,
        max_length: int = 100,
    ) -> Optional[List[tuple[int, int]]]:
        """
        Find shortest path from start to goal.
        
        Returns list of positions from start to goal (inclusive),
        or None if no path exists.
        """
        if self._is_blocked(goal[0], goal[1]):
            return None

        # Priority queue: (priority, position)
        open_set: List[PriorityNode] = []
        heapq.heappush(open_set, PriorityNode(0, start))

        # Track where we came from
        came_from: Dict[tuple[int, int], tuple[int, int]] = {}

        # Cost so far
        g_score: Dict[tuple[int, int], float] = {start: 0}

        while open_set:
            current_node = heapq.heappop(open_set)
            current = current_node.position

            if current == goal:
                return self._reconstruct_path(came_from, current)

            # Check max length
            if len(g_score) >= max_length:
                continue

            for neighbor in self._get_neighbors(current, allow_diagonal):
                tentative_g = g_score[current] + self._heuristic(current, neighbor)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, PriorityNode(f_score, neighbor))

        return None  # No path found

    def _get_neighbors(
        self, pos: tuple[int, int], allow_diagonal: bool
    ) -> List[tuple[int, int]]:
        """Get valid neighboring positions."""
        x, y = pos
        neighbors = []

        # Cardinal directions
        cardinal = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
        # Diagonal directions
        diagonal = [(x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1)]

        directions = cardinal + (diagonal if allow_diagonal else [])

        for nx, ny in directions:
            if not self._is_blocked(nx, ny):
                neighbors.append((nx, ny))

        return neighbors

    def _heuristic(
        self, a: tuple[int, int], b: tuple[int, int], allow_diagonal: bool = True
    ) -> float:
        """Calculate heuristic distance between two points."""
        dx = abs(b[0] - a[0])
        dy = abs(b[1] - a[1])

        if allow_diagonal:
            # Octile distance (allows diagonal movement)
            return max(dx, dy) + (min(dx, dy) * 0.41)  # sqrt(2) ≈ 1.41
        else:
            # Manhattan distance
            return dx + dy

    def _reconstruct_path(
        self, came_from: Dict[tuple[int, int], tuple[int, int]], current: tuple[int, int]
    ) -> List[tuple[int, int]]:
        """Reconstruct path from came_from map."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def find_path_to_adjacent(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        allow_diagonal: bool = True,
    ) -> Optional[List[tuple[int, int]]]:
        """
        Find path to any tile adjacent to goal.
        Useful for melee attackers.
        """
        # Get all adjacent positions to goal
        gx, gy = goal
        adjacent_positions = [
            (gx, gy - 1),  # up
            (gx, gy + 1),  # down
            (gx - 1, gy),  # left
            (gx + 1, gy),  # right
        ]

        if allow_diagonal:
            adjacent_positions.extend([
                (gx - 1, gy - 1),
                (gx + 1, gy - 1),
                (gx - 1, gy + 1),
                (gx + 1, gy + 1),
            ])

        # Try to find path to each adjacent position
        best_path: Optional[List[tuple[int, int]]] = None
        best_length = float("inf")

        for adj_pos in adjacent_positions:
            if not self._is_blocked(adj_pos[0], adj_pos[1]):
                path = self.find_path(start, adj_pos, allow_diagonal)
                if path and len(path) < best_length:
                    best_path = path
                    best_length = len(path)

        return best_path

    def get_distance(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        allow_diagonal: bool = True,
    ) -> float:
        """Get approximate distance between two points."""
        return self._heuristic(start, goal, allow_diagonal)
