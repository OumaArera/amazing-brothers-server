"""
Dashboard API views.

Endpoints
---------
GET /api/dashboard/caregiver/   → CaregiverDashboardView
GET /api/dashboard/manager/     → ManagerDashboardView
"""

from datetime import date, datetime

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.appointment import Appointment
from ..models.branch import Branch
from ..models.branch_manager import BranchManager
from ..models.care import ResidentDailyChart
from ..models.facility import Facility
from ..models.grocery import GroceryRequest
from ..models.leave import LeaveRequest
from ..models.resident import Resident
from ..models.sleep import SleepPattern
from ..models.update import Update
from ..models.utility import UtilityRequest
from ..models.vital import Vital

User = get_user_model()


# ──────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────────────────────────────────────

def _current_shift() -> str:
    h = datetime.now().hour
    if h < 14:
        return "Morning"
    if h < 22:
        return "Afternoon"
    return "Night"


def _time_since(dt) -> str:
    """Human-readable relative time string (e.g. '2h ago', 'Yesterday')."""
    from django.utils import timezone

    delta = timezone.now() - dt
    minutes = int(delta.total_seconds() // 60)

    if minutes < 60:
        return f"{minutes}m ago"
    if minutes < 1_440:
        return f"{minutes // 60}h ago"
    if minutes < 2_880:
        return "Yesterday"
    return f"{delta.days}d ago"


# ──────────────────────────────────────────────────────────────────────────────
# Caregiver helpers
# ──────────────────────────────────────────────────────────────────────────────

def _fetch_today_completion(resident_ids: list, caregiver, today: date) -> tuple[set, set, set]:
    """
    Return three sets of resident IDs that have today's record completed.
    Uses 3 bulk queries regardless of resident count.
    """
    charted_ids = set(
        ResidentDailyChart.objects.filter(
            resident_id__in=resident_ids,
            date=today,
            created_by=caregiver,
        ).values_list("resident_id", flat=True)
    )

    vitals_ids = set(
        Vital.objects.filter(
            resident_id__in=resident_ids,
            date_taken=today,
            caregiver=caregiver,
        ).values_list("resident_id", flat=True)
    )

    sleep_ids = set(
        SleepPattern.objects.filter(
            resident_id__in=resident_ids,
            date=today,
        ).values_list("resident_id", flat=True)
    )

    return charted_ids, vitals_ids, sleep_ids


def _serialize_residents(residents, charted_ids: set, vitals_ids: set, sleep_ids: set) -> list:
    result = []
    for r in residents:
        charted = r.id in charted_ids
        vitals_done = r.id in vitals_ids
        sleep_done = r.id in sleep_ids

        result.append(
            {
                "id": str(r.id),
                "name": f"{r.first_name} {r.last_name}",
                "initials": f"{r.first_name[0]}{r.last_name[0]}".upper(),
                "room": r.room,
                "branch": r.branch.name if r.branch else None,
                "branch_id": str(r.branch_id) if r.branch_id else None,
                "charted_today": charted,
                "vitals_today": vitals_done,
                "sleep_logged_today": sleep_done,
                # alert if any daily item is still outstanding
                "alert": not charted or not vitals_done,
            }
        )
    return result


def _build_task_checklist(residents, charted_ids: set, vitals_ids: set, sleep_ids: set) -> list:
    """
    Build the today's-tasks list from resident records.
    Each resident contributes three task items: care chart, vitals, sleep log.
    """
    tasks = []
    for r in residents:
        short = f"{r.first_name} {r.last_name[0]}."
        rid = r.id

        tasks.extend(
            [
                {
                    "label": f"Care chart — {short}",
                    "done": rid in charted_ids,
                    "type": "care_chart",
                    "resident_id": str(rid),
                    "path": "/caregiver/care-charts",
                },
                {
                    "label": f"Record vitals — {short}",
                    "done": rid in vitals_ids,
                    "type": "vitals",
                    "resident_id": str(rid),
                    "path": "/caregiver/vitals",
                },
                {
                    "label": f"Sleep log — {short}",
                    "done": rid in sleep_ids,
                    "type": "sleep_log",
                    "resident_id": str(rid),
                    "path": "/caregiver/sleep",
                },
            ]
        )
    return tasks


# ──────────────────────────────────────────────────────────────────────────────
# Caregiver Dashboard View
# ──────────────────────────────────────────────────────────────────────────────

class CaregiverDashboardView(APIView):
    """
    GET /api/dashboard/caregiver/

    Returns all data required to render the caregiver dashboard:
      - user info & current shift
      - resident list with today's care/vitals/sleep completion flags
      - task checklist with done/pending state
      - summary stats

    NOTE: Residents are currently scoped to *all active residents*.
    Once a Caregiver → Branch assignment model is added, filter by:
        Resident.objects.filter(branch_id__in=caregiver_branch_ids, active=True)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()

        residents = list(
            Resident.objects.filter(active=True)
            .select_related("branch")
            .order_by("first_name", "last_name")
        )
        resident_ids = [r.id for r in residents]

        # 3 bulk queries cover all residents
        charted_ids, vitals_ids, sleep_ids = _fetch_today_completion(
            resident_ids, user, today
        )

        resident_payloads = _serialize_residents(
            residents, charted_ids, vitals_ids, sleep_ids
        )
        tasks = _build_task_checklist(residents, charted_ids, vitals_ids, sleep_ids)

        tasks_done = sum(1 for t in tasks if t["done"])
        needs_attention = sum(1 for r in resident_payloads if r["alert"])
        pending_charts = sum(1 for r in resident_payloads if not r["charted_today"])

        return Response(
            {
                "user": {
                    "id": str(user.id),
                    "full_name": f"{user.first_name} {user.last_name}",
                    "first_name": user.first_name,
                    "role": user.role,
                },
                "shift": _current_shift(),
                "date": today.isoformat(),
                "stats": {
                    "my_residents": len(residents),
                    "tasks_done": tasks_done,
                    "tasks_total": len(tasks),
                    "needs_attention": needs_attention,
                    "pending_charts": pending_charts,
                },
                "residents": resident_payloads,
                "tasks": tasks,
            }
        )


# ──────────────────────────────────────────────────────────────────────────────
# Manager pending-review helpers  (each returns a list, max `limit` items)
# ──────────────────────────────────────────────────────────────────────────────

def _pending_care_charts(resident_ids: list, limit: int = 20) -> list:
    qs = (
        ResidentDailyChart.objects.filter(
            status="pending",
            resident_id__in=resident_ids,
        )
        .select_related("created_by", "resident")
        .order_by("-created_at")[:limit]
    )
    return [
        {
            "id": str(c.id),
            "type": "Care Chart",
            "staff": (
                f"{c.created_by.first_name} {c.created_by.last_name}"
                if c.created_by
                else "—"
            ),
            "resident": str(c.resident),
            "created_at": c.created_at.isoformat(),
            "time_since": _time_since(c.created_at),
            "path": "/manager/care-charts",
            "color": "#7c3aed",
        }
        for c in qs
    ]


def _pending_vitals(resident_ids: list, limit: int = 20) -> list:
    qs = (
        Vital.objects.filter(
            status=Vital.Status.PENDING,
            resident_id__in=resident_ids,
        )
        .select_related("caregiver", "resident")
        .order_by("-created_at")[:limit]
    )
    return [
        {
            "id": str(v.id),
            "type": "Vitals",
            "staff": (
                f"{v.caregiver.first_name} {v.caregiver.last_name}"
                if v.caregiver
                else "—"
            ),
            "resident": str(v.resident),
            "created_at": v.created_at.isoformat(),
            "time_since": _time_since(v.created_at),
            "path": "/manager/vitals",
            "color": "#0891b2",
        }
        for v in qs
    ]


def _pending_leave_requests(limit: int = 20) -> list:
    qs = (
        LeaveRequest.objects.filter(status="pending")
        .select_related("staff")
        .order_by("-created_at")[:limit]
    )
    return [
        {
            "id": str(lr.id),
            "type": "Leave Request",
            "staff": f"{lr.staff.first_name} {lr.staff.last_name}",
            "resident": "—",
            "created_at": lr.created_at.isoformat(),
            "time_since": _time_since(lr.created_at),
            "path": "/manager/leave",
            "color": "#f59e0b",
        }
        for lr in qs
    ]


def _pending_grocery_requests(branch_ids: list, limit: int = 20) -> list:
    filters = {"status": "pending"}
    if branch_ids:
        filters["branch_id__in"] = branch_ids

    qs = (
        GroceryRequest.objects.filter(**filters)
        .select_related("requested_by", "branch")
        .order_by("-created_at")[:limit]
    )
    return [
        {
            "id": str(g.id),
            "type": "Grocery Request",
            "staff": (
                f"{g.requested_by.first_name} {g.requested_by.last_name}"
                if g.requested_by
                else "—"
            ),
            "resident": "—",
            "created_at": g.created_at.isoformat(),
            "time_since": _time_since(g.created_at),
            "path": "/manager/groceries",
            "color": "#84cc16",
        }
        for g in qs
    ]


def _pending_utility_requests(branch_ids: list, limit: int = 20) -> list:
    filters = {"status__in": ["reported", "acknowledged"]}
    if branch_ids:
        filters["branch_id__in"] = branch_ids

    qs = (
        UtilityRequest.objects.filter(**filters)
        .select_related("reported_by", "branch")
        .order_by("-created_at")[:limit]
    )
    return [
        {
            "id": str(u.id),
            "type": "Utility Request",
            "staff": (
                f"{u.reported_by.first_name} {u.reported_by.last_name}"
                if u.reported_by
                else "—"
            ),
            "resident": "—",
            "created_at": u.created_at.isoformat(),
            "time_since": _time_since(u.created_at),
            "path": "/manager/utilities",
            "color": "#64748b",
        }
        for u in qs
    ]


def _pending_resident_updates(resident_ids: list, limit: int = 20) -> list:
    qs = (
        Update.objects.filter(
            status="pending",
            resident_id__in=resident_ids,
        )
        .select_related("care_giver", "resident")
        .order_by("-created_at")[:limit]
    )
    return [
        {
            "id": str(u.id),
            "type": "Resident Update",
            "staff": (
                f"{u.care_giver.first_name} {u.care_giver.last_name}"
                if u.care_giver
                else "—"
            ),
            "resident": str(u.resident),
            "created_at": u.created_at.isoformat(),
            "time_since": _time_since(u.created_at),
            "path": "/manager/updates",
            "color": "#ec4899",
        }
        for u in qs
    ]


def _pending_appointments(resident_ids: list, today: date, limit: int = 20) -> list:
    """Upcoming appointments for residents in scope."""
    qs = (
        Appointment.objects.filter(
            resident_id__in=resident_ids,
            date_taken__gte=today,
        )
        .select_related("resident")
        .order_by("date_taken")[:limit]
    )
    return [
        {
            "id": str(a.id),
            "type": "Appointment",
            "staff": "—",
            "resident": str(a.resident),
            "created_at": a.created_at.isoformat(),
            "time_since": _time_since(a.created_at),
            "path": "/manager/appointments",
            "color": "#06b6d4",
        }
        for a in qs
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Manager Dashboard View
# ──────────────────────────────────────────────────────────────────────────────

class ManagerDashboardView(APIView):
    """
    GET /api/dashboard/manager/

    Returns all data required to render the manager dashboard:
      - user info & stats
      - pending reviews list (merged, sorted by recency)
      - per-category pending counts
      - managed branches

    Branch scoping:
      If the requesting user has BranchManager records, results are scoped to
      those branches.  Admins with no BranchManager records see everything.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()

        # Branches this manager oversees
        manager_branches = list(
            BranchManager.objects.filter(user=user).select_related("branch__facility")
        )
        branch_ids = [bm.branch_id for bm in manager_branches]

        # Resident scope
        resident_qs = Resident.objects.filter(active=True)
        if branch_ids:
            resident_qs = resident_qs.filter(branch_id__in=branch_ids)
        resident_ids = list(resident_qs.values_list("id", flat=True))

        # Collect pending items per category
        care_charts = _pending_care_charts(resident_ids)
        vitals = _pending_vitals(resident_ids)
        leave = _pending_leave_requests()
        groceries = _pending_grocery_requests(branch_ids)
        utilities = _pending_utility_requests(branch_ids)
        updates = _pending_resident_updates(resident_ids)
        appointments = _pending_appointments(resident_ids, today)

        pending_breakdown = {
            "care_charts": len(care_charts),
            "vitals": len(vitals),
            "leave_requests": len(leave),
            "grocery_requests": len(groceries),
            "utility_requests": len(utilities),
            "resident_updates": len(updates),
            "upcoming_appointments": len(appointments),
        }

        # Merge all reviewable items and sort by recency
        all_pending = sorted(
            care_charts + vitals + leave + groceries + utilities + updates,
            key=lambda x: x["created_at"],
            reverse=True,
        )

        total_pending = sum(
            v for k, v in pending_breakdown.items() if k != "upcoming_appointments"
        )

        staff_count = User.objects.filter(
            role__in=["caregiver", "supervisor"], is_active=True
        ).count()

        return Response(
            {
                "user": {
                    "id": str(user.id),
                    "full_name": f"{user.first_name} {user.last_name}",
                    "first_name": user.first_name,
                    "role": user.role,
                },
                "date": today.isoformat(),
                "stats": {
                    "residents": len(resident_ids),
                    "staff": staff_count,
                    "pending_reviews": total_pending,
                    "facilities": Facility.objects.count(),
                    "branches": Branch.objects.count(),
                },
                "branches": [
                    {
                        "id": str(bm.branch.id),
                        "name": bm.branch.name,
                        "facility": bm.branch.facility.name,
                    }
                    for bm in manager_branches
                ],
                "pending_reviews": all_pending,
                "pending_breakdown": pending_breakdown,
                "upcoming_appointments": appointments,
            }
        )