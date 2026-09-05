# -*- coding: utf-8 -*-
# src/schemas/recommendation_schema.py
"""Pydantic schemas for parliamentary action recommendations (Sprint 6)."""

from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


class UrgencyLevel(str, Enum):
    HIGH = "HIGH"      # Isu darurat / krisis nasional
    MEDIUM = "MEDIUM"  # Isu penting yang sedang berkembang
    LOW = "LOW"        # Isu rutin pemantauan


class RecommendationItem(BaseModel):
    """Format baku draf rekomendasi aksi parlemen DPR RI."""

    akd_name: str = Field(..., description="Nama Komisi/Badan (misal: Komisi XII, Komisi XI)")
    issue_title: str = Field(..., description="Judul isu berita yang direspons")
    action_type: str = Field(..., description="Bentuk aksi (misal: RDP, Kunjungan Kerja, Rilis Pers, Panja)")
    urgency: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM, description="Tingkat urgensi")
    target_stakeholders: list[str] = Field(default_factory=list, description="Daftar kementerian / mitra yang dipanggil")
    action_summary: str = Field(..., description="Uraian langkah konkret yang disarankan")
    policy_background: str = Field(..., description="Latar belakang masalah dan sentimen publik")
    md3_legal_basis: str = Field(default="", description="Pasal wewenang pengawasan di UU MD3")
    status: str = Field(default="draft", description="Status workflow: draft, reviewed, published")
    critique_score: float = Field(default=0.0, description="Nilai kelayakan mutu dari audit mandiri (0.0 - 1.0)")
    critique_iterations: int = Field(default=1, description="Jumlah putaran revisi otomatis yang terjadi")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
