from decimal import Decimal
from io import BytesIO

from django.db.models import CharField, F, Sum, UUIDField, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from apps.core.utils import DefaultPagination
from apps.crm.models import Customer
from apps.crm.serializers import (
    CustomerDueReportFilterSerializer,
    CustomerDueReportItemSerializer,
)
from apps.sales.models import DueCollection, DueSell

_REPORT_FILTER_PARAMS = [
    OpenApiParameter(
        name="customer",
        description="Customer UUID",
        required=True,
        type=str,
    ),
    OpenApiParameter(
        name="start_date",
        description="Start date (YYYY-MM-DD)",
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name="end_date",
        description="End date (YYYY-MM-DD)",
        required=False,
        type=str,
    ),
]


def _build_due_report_querysets(filters):
    customer = get_object_or_404(Customer, id=filters["customer"])
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    due_sell_qs = DueSell.objects.select_related("deliver_by", "order").filter(
        customer=customer
    )
    due_collection_qs = DueCollection.objects.select_related("collected_by").filter(
        customer=customer
    )

    if start_date:
        due_sell_qs = due_sell_qs.filter(sale_date__gte=start_date)
        due_collection_qs = due_collection_qs.filter(collection_date__gte=start_date)

    if end_date:
        due_sell_qs = due_sell_qs.filter(sale_date__lte=end_date)
        due_collection_qs = due_collection_qs.filter(collection_date__lte=end_date)

    due_sell_entries = (
        due_sell_qs.order_by()
        .annotate(
            entry_type=Value("due_sell", output_field=CharField()),
            entry_date=F("sale_date"),
            performed_by=Concat(
                F("deliver_by__first_name"),
                Value(" "),
                F("deliver_by__last_name"),
                output_field=CharField(),
            ),
            order_number=F("order__order_number"),
        )
        .values(
            "id",
            "entry_type",
            "entry_date",
            "amount",
            "note",
            "performed_by",
            "order_id",
            "order_number",
            "created_at",
        )
    )

    due_collection_entries = (
        due_collection_qs.order_by()
        .annotate(
            entry_type=Value("due_collection", output_field=CharField()),
            entry_date=F("collection_date"),
            performed_by=Concat(
                F("collected_by__first_name"),
                Value(" "),
                F("collected_by__last_name"),
                output_field=CharField(),
            ),
            order_id=Value(None, output_field=UUIDField()),
            order_number=Value(None, output_field=CharField()),
        )
        .values(
            "id",
            "entry_type",
            "entry_date",
            "amount",
            "note",
            "performed_by",
            "order_id",
            "order_number",
            "created_at",
        )
    )

    merged_entries_qs = due_sell_entries.union(
        due_collection_entries, all=True
    ).order_by("-entry_date", "-created_at")

    period_due_sell = due_sell_qs.aggregate(total=Sum("amount"))["total"] or Decimal(
        "0.00"
    )
    period_due_collection = due_collection_qs.aggregate(total=Sum("amount"))[
        "total"
    ] or Decimal("0.00")

    return {
        "customer": customer,
        "merged_entries_qs": merged_entries_qs,
        "period_due_sell": period_due_sell,
        "period_due_collection": period_due_collection,
        "start_date": start_date,
        "end_date": end_date,
    }


def _pdf_escape(text):
    if text is None:
        return ""
    s = str(text)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _fmt_money(value):
    if value is None:
        v = Decimal("0")
    elif isinstance(value, str):
        v = Decimal(value)
    else:
        v = value
    return f"{v:.2f}"


def _customer_shop_display(customer):
    """Prefer English shop name for reports; fall back to primary shop_name."""
    en = getattr(customer, "shop_name_en", None)
    if en is not None and str(en).strip():
        return str(en).strip()
    sn = getattr(customer, "shop_name", None)
    return (str(sn).strip() if sn else "")


def _render_customer_due_report_pdf(customer, rows, summary, start_date, end_date):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Customer statement",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="ReportTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=4 * mm,
        textColor=colors.HexColor("#1a237e"),
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        name="ReportSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#424242"),
        alignment=TA_CENTER,
        spaceAfter=6 * mm,
    )
    meta_style = ParagraphStyle(
        name="ReportMeta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#37474f"),
        alignment=TA_LEFT,
        leading=12,
    )

    story = []
    story.append(Paragraph(_pdf_escape("Customer statement"), title_style))
    shop_display = _customer_shop_display(customer)
    subtitle_bits = [x for x in (shop_display, customer.name) if x]
    subtitle_text = " — ".join(subtitle_bits) if subtitle_bits else "Customer report"
    story.append(Paragraph(_pdf_escape(subtitle_text), subtitle_style))

    meta_lines = []
    if shop_display:
        meta_lines.append(f"<b>Shop name:</b> {_pdf_escape(shop_display)}")
    if customer.name:
        meta_lines.append(f"<b>Customer name:</b> {_pdf_escape(customer.name)}")
    meta_lines.extend(
        [
            f"<b>Customer ID:</b> {_pdf_escape(customer.customer_id)}",
            f"<b>Contact:</b> {_pdf_escape(customer.contact_number)}",
            f"<b>Address:</b> {_pdf_escape(customer.address)}",
        ]
    )
    if start_date or end_date:
        meta_lines.append(
            "<b>Period:</b> "
            f"{_pdf_escape(start_date or '—')} to {_pdf_escape(end_date or '—')}"
        )
    story.append(Paragraph("<br/>".join(meta_lines), meta_style))
    story.append(Spacer(1, 5 * mm))

    summary_data = [
        ["Opening balance", _fmt_money(summary["opening_balance"])],
        ["Due sales (period)", _fmt_money(summary["period_due_sell"])],
        ["Collections (period)", _fmt_money(summary["period_due_collection"])],
        ["Net change (period)", _fmt_money(summary["period_net_change"])],
        ["Current balance", _fmt_money(summary["current_balance"])],
    ]
    summary_table = Table(summary_data, colWidths=[72 * mm, 48 * mm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eceff1")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#263238")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#90a4ae")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.white),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#ffebee")),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#e8f5e9")),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 6 * mm))

    entry_labels = {"due_sell": "Due sale", "due_collection": "Due collection"}
    table_header = ["Date", "Type", "Amount", "Order", "By", "Note"]
    table_rows = [table_header]
    row_entry_types = []
    for item in rows:
        et = item.get("entry_type") or ""
        row_entry_types.append(et)
        label = entry_labels.get(et, et)
        order_no = item.get("order_number") or "—"
        note = (item.get("note") or "") or "—"
        if len(note) > 120:
            note = note[:117] + "..."
        performed = (item.get("performed_by") or "") or "—"
        if len(performed) > 28:
            performed = performed[:25] + "..."
        table_rows.append(
            [
                str(item.get("entry_date") or ""),
                label,
                _fmt_money(item.get("amount")),
                str(order_no),
                str(performed),
                str(note),
            ]
        )

    col_widths = [22 * mm, 24 * mm, 24 * mm, 22 * mm, 32 * mm, 52 * mm]
    main_table = Table(table_rows, colWidths=col_widths, repeatRows=1)

    collection_bg = colors.HexColor("#e8f5e9")
    collection_fg = colors.HexColor("#1b5e20")
    due_sell_bg = colors.HexColor("#ffebee")
    due_sell_fg = colors.HexColor("#b71c1c")
    neutral_bg = colors.HexColor("#fafafa")
    neutral_fg = colors.HexColor("#37474f")

    table_style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bdbdbd")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for i, et in enumerate(row_entry_types, start=1):
        if et == "due_collection":
            table_style_cmds.append(("BACKGROUND", (0, i), (-1, i), collection_bg))
            table_style_cmds.append(("TEXTCOLOR", (0, i), (-1, i), collection_fg))
        elif et == "due_sell":
            table_style_cmds.append(("BACKGROUND", (0, i), (-1, i), due_sell_bg))
            table_style_cmds.append(("TEXTCOLOR", (0, i), (-1, i), due_sell_fg))
        else:
            table_style_cmds.append(("BACKGROUND", (0, i), (-1, i), neutral_bg))
            table_style_cmds.append(("TEXTCOLOR", (0, i), (-1, i), neutral_fg))

    main_table.setStyle(TableStyle(table_style_cmds))
    story.append(main_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


@extend_schema(
    tags=["Customer Reports"],
    description=(
        "Get merged DueSell(due_sell) and DueCollection(due_collection) entries for one customer. "
        "Supports date range filtering and pagination."
    ),
    parameters=[
        *_REPORT_FILTER_PARAMS,
        OpenApiParameter(
            name="page",
            description="Page number",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="page_size",
            description="Items per page",
            required=False,
            type=int,
        ),
    ],
)
class CustomerDueReportViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Merged due report for a specific customer.
    Combines DueSell and DueCollection records in a single paginated timeline.
    """

    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    queryset = Customer.objects.none()
    serializer_class = CustomerDueReportItemSerializer

    def list(self, request, *args, **kwargs):
        filter_serializer = CustomerDueReportFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        ctx = _build_due_report_querysets(filter_serializer.validated_data)

        customer = ctx["customer"]
        start_date = ctx["start_date"]
        end_date = ctx["end_date"]
        merged_entries_qs = ctx["merged_entries_qs"]
        period_due_sell = ctx["period_due_sell"]
        period_due_collection = ctx["period_due_collection"]

        page = self.paginate_queryset(merged_entries_qs)
        serializer = self.get_serializer(page, many=True)
        paginated_response = self.get_paginated_response(serializer.data)
        paginated_response.data["customer"] = {
            "id": str(customer.id),
            "customer_id": customer.customer_id,
            "name": customer.name,
            "shop_name": _customer_shop_display(customer),
            "contact_number": customer.contact_number,
            "address": customer.address,
        }
        paginated_response.data["summary"] = {
            "opening_balance": customer.opening_balance,
            "period_due_sell": period_due_sell,
            "period_due_collection": period_due_collection,
            "period_net_change": period_due_collection - period_due_sell,
            "current_balance": customer.balance,
        }
        paginated_response.data["date_range"] = {
            "start_date": start_date,
            "end_date": end_date,
        }
        return paginated_response

    @extend_schema(
        summary="Download customer due report (PDF)",
        description=(
            "Same filters as the list endpoint. Returns a formatted PDF with the full "
            "merged timeline (no API pagination)."
        ),
        parameters=_REPORT_FILTER_PARAMS,
        responses={200: OpenApiResponse(description="PDF document")},
    )
    @action(detail=False, methods=["get"], url_path="download-pdf")
    def download_pdf(self, request):
        filter_serializer = CustomerDueReportFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        ctx = _build_due_report_querysets(filter_serializer.validated_data)

        customer = ctx["customer"]
        all_rows = list(ctx["merged_entries_qs"])
        serializer = self.get_serializer(all_rows, many=True)

        period_due_sell = ctx["period_due_sell"]
        period_due_collection = ctx["period_due_collection"]
        summary = {
            "opening_balance": customer.opening_balance,
            "period_due_sell": period_due_sell,
            "period_due_collection": period_due_collection,
            "period_net_change": period_due_collection - period_due_sell,
            "current_balance": customer.balance,
        }

        pdf_bytes = _render_customer_due_report_pdf(
            customer,
            serializer.data,
            summary,
            ctx["start_date"],
            ctx["end_date"],
        )
        safe_id = str(customer.customer_id or customer.id).replace("/", "-")
        filename = f"customer_statement_{safe_id}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
