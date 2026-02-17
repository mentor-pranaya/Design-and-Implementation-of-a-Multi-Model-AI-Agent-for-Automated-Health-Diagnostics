"""
Report Generation Module
Formats the final output into a clear, user-friendly HTML report
"""

from typing import Dict, Any
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate formatted HTML health report"""

    STATUS_COLORS = {
        'healthy':       '#27ae60',
        'monitor':       '#2980b9',
        'needs_attention': '#f39c12',
        'high_concern':  '#e67e22',
        'critical':      '#e74c3c'
    }

    STATUS_ICONS = {
        'healthy':         '✅',
        'monitor':         '🔵',
        'needs_attention': '⚠️',
        'high_concern':    '🟠',
        'critical':        '🔴'
    }

    PARAM_ICONS = {
        'normal':         '✅',
        'high':           '⬆️',
        'low':            '⬇️',
        'borderline_high': '⚠️',
        'borderline_low':  '⚠️',
        'critical_high':  '🔴',
        'critical_low':   '🔴'
    }

    # ------------------------------------------------------------------
    def generate_html_report(self, report: Dict[str, Any],
                              output_path: str = None) -> str:
        """Generate complete HTML report"""

        meta   = report.get('metadata', {})
        status = report.get('overall_status', 'unknown')
        color  = self.STATUS_COLORS.get(status, '#95a5a6')
        icon   = self.STATUS_ICONS.get(status, '❓')

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Health Report – {meta.get('report_id','')}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #f0f2f5;
         color: #2c3e50; padding: 20px; }}
  .container {{ max-width: 960px; margin: auto; }}
  .header {{ background: linear-gradient(135deg,#2c3e50,#3498db);
             color: white; padding: 30px; border-radius: 12px;
             margin-bottom: 20px; }}
  .header h1 {{ font-size: 1.8rem; }}
  .header p  {{ opacity: .85; margin-top: 4px; }}
  .status-badge {{ display:inline-block; padding:8px 18px;
                   border-radius:20px; font-weight:700;
                   background:{color}; color:white;
                   margin-top:12px; font-size:.95rem; }}
  .card {{ background:white; border-radius:12px;
           padding:24px; margin-bottom:20px;
           box-shadow:0 2px 8px rgba(0,0,0,.07); }}
  .card h2 {{ font-size:1.15rem; color:#2c3e50;
              margin-bottom:16px; padding-bottom:8px;
              border-bottom:2px solid #3498db; }}
  .info-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }}
  .info-item {{ background:#f8f9fa; padding:12px; border-radius:8px; }}
  .info-item .label {{ font-size:.75rem; color:#7f8c8d;
                        text-transform:uppercase; }}
  .info-item .value {{ font-weight:600; margin-top:2px; }}
  table {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
  th {{ background:#2c3e50; color:white; padding:10px 14px;
        text-align:left; }}
  td {{ padding:10px 14px; border-bottom:1px solid #ecf0f1; }}
  tr:hover td {{ background:#f8f9fa; }}
  .tag {{ display:inline-block; padding:3px 10px; border-radius:12px;
          font-size:.78rem; font-weight:600; color:white; }}
  .tag-normal         {{ background:#27ae60; }}
  .tag-high           {{ background:#e74c3c; }}
  .tag-low            {{ background:#e67e22; }}
  .tag-borderline_high{{ background:#f39c12; }}
  .tag-borderline_low {{ background:#f39c12; }}
  .tag-critical_high  {{ background:#8e44ad; }}
  .tag-critical_low   {{ background:#8e44ad; }}
  .pattern-card {{ background:#eaf4fd; border-left:4px solid #3498db;
                   padding:14px; border-radius:0 8px 8px 0;
                   margin-bottom:10px; }}
  .risk-bar-wrap {{ background:#ecf0f1; border-radius:8px;
                    height:12px; margin:6px 0; overflow:hidden; }}
  .risk-bar {{ height:100%; border-radius:8px;
               transition:width .5s; }}
  .rec-category {{ margin-bottom:18px; }}
  .rec-category h3 {{ font-size:.95rem; color:#2c3e50;
                       margin-bottom:8px; }}
  .rec-item {{ background:#f8f9fa; padding:10px 14px;
               border-radius:6px; margin-bottom:6px;
               border-left:3px solid #3498db; font-size:.88rem; }}
  .monitor-item {{ background:#eafaf1; border-left:4px solid #27ae60;
                   padding:12px; border-radius:0 8px 8px 0;
                   margin-bottom:10px; }}
  .disclaimer {{ background:#fdf2e9; border:1px solid #f0a500;
                 padding:16px; border-radius:8px;
                 font-size:.82rem; color:#7f6000; }}
  @media(max-width:600px){{
    .info-grid{{ grid-template-columns:1fr 1fr; }}
  }}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>🩺 Blood Report Analysis</h1>
    <p>AI-Powered Health Diagnostics System</p>
    <div class="status-badge">{icon} {status.replace('_',' ').title()}</div>
  </div>

  <!-- Patient Info -->
  <div class="card">
    <h2>👤 Patient Information</h2>
    <div class="info-grid">
      <div class="info-item">
        <div class="label">Report ID</div>
        <div class="value">{meta.get('report_id','—')}</div>
      </div>
      <div class="info-item">
        <div class="label">Patient ID</div>
        <div class="value">{meta.get('patient_id','—')}</div>
      </div>
      <div class="info-item">
        <div class="label">Test Date</div>
        <div class="value">{meta.get('test_date','—')}</div>
      </div>
      <div class="info-item">
        <div class="label">Laboratory</div>
        <div class="value">{meta.get('lab_name','—')}</div>
      </div>
      <div class="info-item">
        <div class="label">Gender</div>
        <div class="value">{str(meta.get('gender','—')).title()}</div>
      </div>
      <div class="info-item">
        <div class="label">Age</div>
        <div class="value">{meta.get('age','—')}</div>
      </div>
    </div>
  </div>

  {self._parameter_table(report)}
  {self._patterns_section(report)}
  {self._risk_section(report)}
  {self._recommendations_section(report)}
  {self._monitoring_section(report)}

  <!-- Disclaimer -->
  <div class="disclaimer">
    ⚠️ <strong>Medical Disclaimer:</strong>
    This report is generated by an AI system for educational purposes only.
    It does not constitute medical advice, diagnosis, or treatment.
    Always consult a qualified healthcare professional for medical decisions.
  </div>

</div>
</body>
</html>"""

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"HTML report saved: {output_path}")

        return html

    # ------------------------------------------------------------------
    def _parameter_table(self, report: Dict[str, Any]) -> str:
        interps = report.get('interpretations', [])
        if not interps:
            return ''

        rows = ''
        for p in interps:
            status = p.get('status', 'normal')
            icon   = self.PARAM_ICONS.get(status, '•')
            dev    = p.get('deviation_percentage', 0)
            dev_str = (f'+{dev:.1f}%' if dev > 0
                       else f'{dev:.1f}%' if dev < 0 else '—')
            rows += f"""
            <tr>
              <td>{icon} {p.get('standard_name','')}</td>
              <td><strong>{p.get('value','')}</strong></td>
              <td>{p.get('unit','')}</td>
              <td>{p.get('reference_min','—')} – {p.get('reference_max','—')}</td>
              <td>{dev_str}</td>
              <td><span class="tag tag-{status}">{status.replace('_',' ').title()}</span></td>
            </tr>"""

        return f"""
  <div class="card">
    <h2>🔬 Parameter Analysis</h2>
    <table>
      <thead>
        <tr>
          <th>Parameter</th><th>Value</th><th>Unit</th>
          <th>Reference Range</th><th>Deviation</th><th>Status</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>"""

    # ------------------------------------------------------------------
    def _patterns_section(self, report: Dict[str, Any]) -> str:
        patterns = report.get('pattern_analysis', {}).get('patterns', [])
        if not patterns:
            return '''
  <div class="card">
    <h2>🔍 Clinical Patterns</h2>
    <p style="color:#7f8c8d">No significant clinical patterns identified.</p>
  </div>'''

        cards = ''
        for p in patterns:
            params_html = ''.join(
                f'<li>{m["parameter"]}: {m["value"]} '
                f'(threshold {m["threshold"]})</li>'
                for m in p.get('matching_parameters', [])
            )
            conf_pct = int(p.get('confidence', 0) * 100)
            cards += f"""
    <div class="pattern-card">
      <strong>🔷 {p.get('description','')}</strong>
      <div style="font-size:.82rem;color:#555;margin:4px 0">
        Confidence: {conf_pct}%
      </div>
      <ul style="margin-left:18px;font-size:.85rem">{params_html}</ul>
    </div>"""

        return f'<div class="card"><h2>🔍 Clinical Patterns</h2>{cards}</div>'

    # ------------------------------------------------------------------
    def _risk_section(self, report: Dict[str, Any]) -> str:
        risk_scores = report.get('pattern_analysis', {}).get('risk_scores', {})
        ratios      = report.get('pattern_analysis', {}).get('ratios', {})

        if not risk_scores and not ratios:
            return ''

        risk_colors = {'low': '#27ae60', 'moderate': '#f39c12', 'high': '#e74c3c'}
        content = ''

        for rtype, rdata in risk_scores.items():
            level     = rdata.get('level', 'low')
            score     = rdata.get('score', 0)
            bar_color = risk_colors.get(level, '#95a5a6')
            content  += f"""
    <div style="margin-bottom:16px">
      <div style="display:flex;justify-content:space-between">
        <strong>{rtype.title()} Risk</strong>
        <span style="color:{bar_color};font-weight:700">
          {level.upper()} ({score}/10)
        </span>
      </div>
      <div class="risk-bar-wrap">
        <div class="risk-bar"
             style="width:{score*10}%;background:{bar_color}"></div>
      </div>
      <div style="font-size:.82rem;color:#555">{rdata.get('description','')}</div>
    </div>"""

        for rname, rdata in ratios.items():
            content += f"""
    <div style="background:#f8f9fa;padding:10px;border-radius:8px;
                margin-bottom:10px;font-size:.88rem">
      <strong>{rdata.get('description','')}</strong>:
      {rdata.get('value','')}
      <span style="color:#7f8c8d"> — {rdata.get('interpretation','')}</span>
    </div>"""

        return f'<div class="card"><h2>📊 Risk Assessment</h2>{content}</div>'

    # ------------------------------------------------------------------
    def _recommendations_section(self, report: Dict[str, Any]) -> str:
        recs = report.get('recommendations', {})

        categories = {
            'immediate_actions': ('🚨 Immediate Actions', '#e74c3c'),
            'medical':           ('🏥 Medical Consultation', '#8e44ad'),
            'dietary':           ('🥗 Dietary Recommendations', '#27ae60'),
            'lifestyle':         ('🏃 Lifestyle Modifications', '#2980b9'),
        }

        content = ''
        for key, (title, color) in categories.items():
            items = recs.get(key, [])
            if not items:
                continue
            items_html = ''
            for item in items:
                text = item.get('action', item) if isinstance(item, dict) else item
                items_html += f'<div class="rec-item">{text}</div>'
            content += f"""
    <div class="rec-category">
      <h3 style="color:{color}">{title}</h3>
      {items_html}
    </div>"""

        if not content:
            content = '<p style="color:#27ae60">✅ No specific recommendations — maintain your healthy lifestyle!</p>'

        return f'<div class="card"><h2>💊 Personalized Recommendations</h2>{content}</div>'

    # ------------------------------------------------------------------
    def _monitoring_section(self, report: Dict[str, Any]) -> str:
        monitoring = report.get('recommendations', {}).get('monitoring', [])
        if not monitoring:
            return ''

        items_html = ''
        for m in monitoring:
            items_html += f"""
    <div class="monitor-item">
      <strong>{m.get('test','')}</strong>
      <div style="font-size:.82rem;color:#555;margin-top:4px">
        📅 Frequency: {m.get('frequency','')} &nbsp;|&nbsp;
        Reason: {m.get('reason','')}
      </div>
    </div>"""

        return f'<div class="card"><h2>📅 Monitoring Plan</h2>{items_html}</div>'