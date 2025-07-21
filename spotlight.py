from flask import Blueprint, render_template, request
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64

spotlight_bp = Blueprint("spotlight", __name__, template_folder="templates")

@spotlight_bp.route("/", methods=["GET", "POST"])
def index():
    chart_uri = None
    if request.method == "POST":
        raw = request.form.get("metrics", "").strip().splitlines()
        data = []
        for line in raw:
            if ":" in line:
                label, val = line.split(":", 1)
                try:
                    data.append((label.strip(), float(val.strip())))
                except:
                    pass
        
        if data:
            # Pareto: sort desc, compute cumulative %
            data.sort(key=lambda x: x[1], reverse=True)
            labels, values = zip(*data)
            cum = [sum(values[:i+1]) / sum(values) * 100 for i in range(len(values))]

            # Apply purple & rose gold theme
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#1A0E36')  # deep indigo background
            ax.set_facecolor('#2C1A4B')  # muted plum surface
            
            # Bar chart with rose gold
            bars = ax.bar(labels, values, color="#B76E79", alpha=0.8, edgecolor="#E6B7C1", linewidth=1)
            
            # Cumulative line with purple
            ax2 = ax.twinx()
            line = ax2.plot(labels, cum, marker='o', color="#7D5BA6", linewidth=3, markersize=8, markerfacecolor="#E6B7C1")
            
            # Styling
            ax.set_ylabel("Count", color="#EDE7F6", fontsize=12, fontweight='bold')
            ax2.set_ylabel("Cumulative %", color="#EDE7F6", fontsize=12, fontweight='bold')
            ax.set_title("Pareto Analysis", color="#FFFFFF", fontsize=16, fontweight='bold', pad=20)
            
            # Customize ticks and labels
            ax.tick_params(axis='both', colors="#EDE7F6")
            ax2.tick_params(axis='both', colors="#EDE7F6")
            ax.set_xticklabels(labels, rotation=45, ha="right", color="#EDE7F6")
            
            # Grid styling
            ax.grid(True, alpha=0.3, color="#B76E79")
            
            plt.tight_layout()

            # Convert to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, facecolor='#1A0E36', edgecolor='none')
            buf.seek(0)
            chart_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
            plt.close(fig)

    return render_template("spotlight.html", chart_uri=chart_uri)