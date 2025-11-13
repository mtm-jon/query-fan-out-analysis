import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

# Page config
st.set_page_config(
    page_title="Query Fan-Out Position Heatmap",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Query Fan-Out Position Heatmap")
st.markdown("**Color-coded position rankings from 1-100+ | Created by Moving Traffic Media**")

# File uploaders
col1, col2 = st.columns(2)

with col1:
    fanout_file = st.file_uploader(
        "📁 Query Fan-Out CSV",
        type=['csv'],
        help="Upload your Qforia output file"
    )

with col2:
    gsc_file = st.file_uploader(
        "📁 Google Search Console CSV",
        type=['csv'],
        help="Upload your GSC Queries file"
    )

# Process files and render visualization
if fanout_file is not None and gsc_file is not None:
    # Read the CSV files
    fanout_df = pd.read_csv(fanout_file)
    gsc_df = pd.read_csv(gsc_file)
    
    # Convert to JSON for JavaScript
    fanout_json = fanout_df.to_json(orient='records')
    gsc_json = gsc_df.to_json(orient='records')
    
    # HTML/JS component
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f172a;
                color: #f8fafc;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 15px;
                margin-bottom: 30px;
            }}
            
            .stat-card {{
                background: #1e293b;
                border-radius: 8px;
                padding: 20px;
                border-left: 4px solid #3b82f6;
            }}
            
            .stat-value {{
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            .stat-label {{
                color: #94a3b8;
                font-size: 14px;
            }}
            
            .legend {{
                background: #1e293b;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 30px;
            }}
            
            .legend-title {{
                font-weight: bold;
                margin-bottom: 15px;
                font-size: 16px;
            }}
            
            .legend-gradient {{
                height: 30px;
                border-radius: 4px;
                margin-bottom: 10px;
                background: linear-gradient(to right, #10b981, #84cc16, #facc15, #fb923c, #f97316, #ef4444, #6b7280);
            }}
            
            .legend-labels {{
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                color: #94a3b8;
            }}
            
            #heatmap {{
                background: #1e293b;
                border-radius: 12px;
                padding: 30px;
                overflow-x: auto;
                margin-bottom: 30px;
            }}
            
            .tooltip {{
                position: absolute;
                padding: 12px;
                background: rgba(15, 23, 42, 0.95);
                border: 1px solid #475569;
                border-radius: 8px;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
                font-size: 13px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
                max-width: 300px;
                z-index: 1000;
            }}
            
            .tooltip-query {{
                font-weight: bold;
                margin-bottom: 8px;
                color: #f8fafc;
                font-size: 14px;
            }}
            
            .tooltip-row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
                color: #cbd5e1;
            }}
            
            .tooltip-label {{
                color: #94a3b8;
            }}
            
            .cell {{
                cursor: pointer;
                transition: all 0.2s;
            }}
            
            .cell:hover {{
                stroke: #fff;
                stroke-width: 2px;
                filter: brightness(1.2);
            }}
            
            .query-label {{
                font-size: 13px;
                fill: #e2e8f0;
            }}
            
            .type-label {{
                font-size: 11px;
                fill: #94a3b8;
            }}
            
            .position-text {{
                font-size: 11px;
                font-weight: bold;
                fill: #fff;
                text-anchor: middle;
                pointer-events: none;
            }}
            
            .axis-label {{
                font-size: 14px;
                font-weight: bold;
                fill: #f8fafc;
            }}
            
            .ai-section {{
                background: linear-gradient(135deg, #1e293b, #0f172a);
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 30px;
                border: 2px solid #3b82f6;
            }}
            
            .ai-section h3 {{
                color: #f8fafc;
                margin-bottom: 15px;
            }}
            
            .ai-buttons {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 10px;
            }}
            
            .ai-btn {{
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                color: white;
            }}
            
            .ai-btn:hover {{
                transform: translateY(-2px);
            }}
            
            .chatgpt-btn {{ background: linear-gradient(135deg, #10a37f, #0e906f); }}
            .claude-btn {{ background: linear-gradient(135deg, #d97757, #c9673f); }}
            .gemini-btn {{ background: linear-gradient(135deg, #4285f4, #3367d6); }}
            .perplexity-btn {{ background: linear-gradient(135deg, #20808d, #1a6d78); }}
            .grok-btn {{ background: linear-gradient(135deg, #000000, #1a1a1a); }}
            
            .prompt-box {{
                background: #1e293b;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 15px;
                color: #cbd5e1;
                font-size: 13px;
                max-height: 200px;
                overflow-y: auto;
                margin-bottom: 15px;
                font-family: monospace;
            }}
        </style>
    </head>
    <body>
        <div id="stats"></div>
        
        <div class="legend">
            <div class="legend-title">Position Color Scale</div>
            <div class="legend-gradient"></div>
            <div class="legend-labels">
                <span>Position 1 (Best)</span>
                <span>Position 20</span>
                <span>Position 50</span>
                <span>Position 100+</span>
                <span>Not Ranking</span>
            </div>
        </div>
        
        <div class="ai-section">
            <h3>🤖 AI-Powered Insights</h3>
            <div class="prompt-box" id="aiPrompt">Analyzing your data...</div>
            <div class="ai-buttons">
                <button class="ai-btn chatgpt-btn" onclick="openAI('chatgpt')">ChatGPT</button>
                <button class="ai-btn claude-btn" onclick="openAI('claude')">Claude</button>
                <button class="ai-btn gemini-btn" onclick="openAI('gemini')">Gemini</button>
                <button class="ai-btn perplexity-btn" onclick="openAI('perplexity')">Perplexity</button>
                <button class="ai-btn grok-btn" onclick="openAI('grok')">Grok</button>
            </div>
        </div>
        
        <div id="heatmap"></div>
        
        <div class="tooltip" id="tooltip"></div>
        
        <script>
            const fanoutData = {fanout_json};
            const gscData = {gsc_json};
            let matchedData = null;
            let generatedPrompt = '';
            
            // Initialize
            processData();
            
            function processData() {{
                matchedData = matchQueries(fanoutData, gscData);
                renderStats(matchedData);
                renderHeatmap(matchedData);
            }}
            
            function matchQueries(fanout, gsc) {{
                const matched = [];
                
                fanout.forEach(fanoutRow => {{
                    const fanoutQuery = fanoutRow.query.toLowerCase().trim();
                    
                    let gscMatch = null;
                    let bestMatchScore = 0;
                    
                    for (let gscRow of gsc) {{
                        const gscQuery = gscRow['Top queries'].toLowerCase().trim();
                        let matchScore = 0;
                        
                        if (gscQuery === fanoutQuery) {{
                            matchScore = 100;
                        }} else {{
                            const fanoutWords = fanoutQuery.split(' ');
                            const gscWords = gscQuery.split(' ');
                            let matchingWords = 0;
                            
                            fanoutWords.forEach(word => {{
                                if (word.length > 2 && gscWords.includes(word)) {{
                                    matchingWords++;
                                }}
                            }});
                            
                            const similarity = matchingWords / Math.max(fanoutWords.length, gscWords.length);
                            const lengthDiff = Math.abs(fanoutQuery.length - gscQuery.length);
                            
                            if (similarity > 0.7 && lengthDiff < 20) {{
                                matchScore = similarity * 90;
                            }}
                        }}
                        
                        if (matchScore > bestMatchScore && matchScore > 50) {{
                            bestMatchScore = matchScore;
                            gscMatch = gscRow;
                        }}
                    }}
                    
                    if (gscMatch) {{
                        matched.push({{
                            fanout_query: fanoutRow.query,
                            type: fanoutRow.type,
                            user_intent: fanoutRow.user_intent,
                            routing_format: fanoutRow.routing_format,
                            position: parseFloat(gscMatch.Position),
                            clicks: parseInt(gscMatch.Clicks),
                            impressions: parseInt(gscMatch.Impressions),
                            ctr: gscMatch.CTR,
                            matched_gsc_query: gscMatch['Top queries'],
                            is_gap: false
                        }});
                    }} else {{
                        matched.push({{
                            fanout_query: fanoutRow.query,
                            type: fanoutRow.type,
                            user_intent: fanoutRow.user_intent,
                            routing_format: fanoutRow.routing_format,
                            position: null,
                            clicks: 0,
                            impressions: 0,
                            ctr: '0%',
                            matched_gsc_query: null,
                            is_gap: true
                        }});
                    }}
                }});
                
                return matched;
            }}
            
            function getPositionColor(position) {{
                if (position === null) return '#374151';
                if (position <= 3) return '#10b981';
                if (position <= 5) return '#84cc16';
                if (position <= 10) return '#facc15';
                if (position <= 15) return '#fbbf24';
                if (position <= 20) return '#fb923c';
                if (position <= 30) return '#f97316';
                if (position <= 50) return '#ef4444';
                return '#dc2626';
            }}
            
            function renderStats(data) {{
                const ranking = data.filter(d => !d.is_gap);
                const gaps = data.filter(d => d.is_gap);
                const top3 = ranking.filter(d => d.position <= 3).length;
                const top10 = ranking.filter(d => d.position <= 10).length;
                const totalClicks = ranking.reduce((sum, d) => sum + d.clicks, 0);
                
                const statsHtml = `
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" style="color: #10b981;">${{ranking.length}}</div>
                            <div class="stat-label">Ranking Queries</div>
                        </div>
                        <div class="stat-card" style="border-left-color: #ef4444;">
                            <div class="stat-value" style="color: #ef4444;">${{gaps.length}}</div>
                            <div class="stat-label">Content Gaps</div>
                        </div>
                        <div class="stat-card" style="border-left-color: #10b981;">
                            <div class="stat-value" style="color: #10b981;">${{top3}}</div>
                            <div class="stat-label">In Top 3</div>
                        </div>
                        <div class="stat-card" style="border-left-color: #3b82f6;">
                            <div class="stat-value" style="color: #3b82f6;">${{top10}}</div>
                            <div class="stat-label">In Top 10</div>
                        </div>
                        <div class="stat-card" style="border-left-color: #f59e0b;">
                            <div class="stat-value" style="color: #f59e0b;">${{totalClicks.toLocaleString()}}</div>
                            <div class="stat-label">Total Clicks</div>
                        </div>
                    </div>
                `;
                
                document.getElementById('stats').innerHTML = statsHtml;
                generateAIPrompt(data, ranking, gaps, top3, top10, totalClicks);
            }}
            
            function generateAIPrompt(data, ranking, gaps, top3, top10, totalClicks) {{
                const topPerformers = ranking.sort((a, b) => a.position - b.position).slice(0, 3);
                
                let prompt = `I'm analyzing my query fan-out strategy. Here are the results:

OVERALL: ${{data.length}} queries analyzed, ${{ranking.length}} ranking, ${{gaps.length}} gaps
TOP 3 POSITIONS: ${{top3}} queries
TOP 10 POSITIONS: ${{top10}} queries
TOTAL CLICKS: ${{totalClicks.toLocaleString()}}

TOP PERFORMERS:
${{topPerformers.map((q, i) => `${{i+1}}. "${{q.fanout_query}}" - Pos ${{q.position.toFixed(1)}} (${{q.clicks}} clicks)`).join('\\n')}}

CONTENT GAPS: ${{gaps.length}} queries not ranking

Please analyze this data and provide:
1. Key patterns in performance
2. Priority content gaps to address
3. Strategic recommendations
4. 30-day action plan`;

                document.getElementById('aiPrompt').textContent = prompt;
                generatedPrompt = prompt;
            }}
            
            function renderHeatmap(data) {{
                const margin = {{top: 80, right: 50, bottom: 50, left: 500}};
                const cellWidth = 600;
                const cellHeight = 35;
                const width = cellWidth + margin.left + margin.right;
                const height = data.length * cellHeight + margin.top + margin.bottom;

                const svg = d3.select('#heatmap')
                    .append('svg')
                    .attr('width', width)
                    .attr('height', height);

                const g = svg.append('g')
                    .attr('transform', `translate(${{margin.left}},${{margin.top}})`);

                const tooltip = d3.select('#tooltip');

                g.append('text')
                    .attr('class', 'axis-label')
                    .attr('x', cellWidth / 2)
                    .attr('y', -20)
                    .attr('text-anchor', 'middle')
                    .text('Position in Google Search Console');

                data.forEach((d, i) => {{
                    const row = g.append('g')
                        .attr('transform', `translate(0,${{i * cellHeight}})`);

                    row.append('text')
                        .attr('class', 'query-label')
                        .attr('x', -10)
                        .attr('y', cellHeight / 2 - 5)
                        .attr('text-anchor', 'end')
                        .text(d.fanout_query.length > 60 ? d.fanout_query.substring(0, 57) + '...' : d.fanout_query);

                    row.append('text')
                        .attr('class', 'type-label')
                        .attr('x', -10)
                        .attr('y', cellHeight / 2 + 10)
                        .attr('text-anchor', 'end')
                        .text(`[${{d.type}}]`);

                    const cell = row.append('rect')
                        .attr('class', 'cell')
                        .attr('x', 0)
                        .attr('y', 0)
                        .attr('width', cellWidth - 2)
                        .attr('height', cellHeight - 2)
                        .attr('rx', 6)
                        .style('fill', getPositionColor(d.position))
                        .style('opacity', d.is_gap ? 0.7 : 0.9);

                    if (d.is_gap) {{
                        row.append('text')
                            .attr('class', 'position-text')
                            .attr('x', cellWidth / 2)
                            .attr('y', cellHeight / 2 + 5)
                            .style('font-size', '16px')
                            .text('CONTENT GAP - NOT RANKING');
                    }} else {{
                        row.append('text')
                            .attr('class', 'position-text')
                            .attr('x', cellWidth / 2)
                            .attr('y', cellHeight / 2 - 5)
                            .style('font-size', '14px')
                            .text(`Position: ${{d.position.toFixed(1)}}`);
                        
                        row.append('text')
                            .attr('class', 'position-text')
                            .attr('x', cellWidth / 2)
                            .attr('y', cellHeight / 2 + 12)
                            .style('font-size', '11px')
                            .style('opacity', 0.9)
                            .text(`${{d.clicks}} clicks | ${{d.impressions.toLocaleString()}} impressions`);
                    }}

                    cell.on('mouseover', function(event) {{
                        tooltip.style('opacity', 1);
                        let content = `<div class="tooltip-query">${{d.fanout_query}}</div>`;
                        
                        if (d.is_gap) {{
                            content += `<div class="tooltip-row"><span class="tooltip-label">Status:</span><span style="color: #ef4444;">CONTENT GAP</span></div>`;
                        }} else {{
                            content += `<div class="tooltip-row"><span class="tooltip-label">Position:</span><span>${{d.position.toFixed(1)}}</span></div>`;
                            content += `<div class="tooltip-row"><span class="tooltip-label">Clicks:</span><span>${{d.clicks}}</span></div>`;
                        }}
                        
                        tooltip.html(content);
                    }})
                    .on('mousemove', function(event) {{
                        tooltip
                            .style('left', (event.pageX + 15) + 'px')
                            .style('top', (event.pageY - 15) + 'px');
                    }})
                    .on('mouseout', function() {{
                        tooltip.style('opacity', 0);
                    }});
                }});
            }}
            
            function openAI(platform) {{
                const urls = {{
                    'chatgpt': 'https://chat.openai.com/',
                    'claude': 'https://claude.ai/',
                    'gemini': 'https://gemini.google.com/',
                    'perplexity': 'https://www.perplexity.ai/',
                    'grok': 'https://x.com/i/grok'
                }};
                
                window.open(urls[platform], '_blank');
                navigator.clipboard.writeText(generatedPrompt);
                alert('✅ Prompt copied! Paste it into ' + platform.charAt(0).toUpperCase() + platform.slice(1));
            }}
        </script>
    </body>
    </html>
    """
    
    # Render the component
    components.html(html_code, height=2000, scrolling=True)
    
    # Attribution
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #1e3a8a, #1e40af); border-radius: 12px; margin: 30px 0;">
        <p style="color: #e0e7ff; font-size: 17px; margin: 0; line-height: 1.8;">
            <strong style="color: white; font-size: 20px;">Created by Jon Clark</strong><br>
            Managing Partner at 
            <a href="https://www.movingtrafficmedia.com" target="_blank" style="color: #93c5fd; text-decoration: none; font-weight: 600; font-size: 17px;">Moving Traffic Media</a>, 
            an AI-driven search agency.
            <br><br>
            <a href="https://www.linkedin.com/in/ppcmarketing" target="_blank" 
               style="display: inline-block; background: #0077b5; color: white; padding: 12px 24px; 
               border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 5px; font-size: 15px;">
               🔗 Follow on LinkedIn
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions section after results
    st.markdown("---")
    st.markdown("### 📖 How to Use This Tool")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1️⃣ Export from Qforia**  
        Go to [Qforia: Query Fan-Out Simulator](https://ipullrank.com/tools/qforia) 
        and export your query fan-out results.
        
        **3️⃣ Upload Your Files**  
        Use the upload boxes at the top to upload both CSV files.
        
        **5️⃣ Get AI Analysis**  
        Click any AI assistant button to get strategic recommendations.
        """)
    
    with col2:
        st.markdown("""
        **2️⃣ Export from Google Search Console**  
        In Google Search Console, search for your head term and export the "Queries" file.
        
        **4️⃣ Review Results**  
        Check the stats, AI insights, and three heatmaps above.
        
        **6️⃣ Export & Act**  
        Use the insights to prioritize your content calendar.
        """)
    
    # Color guide
    st.markdown("### 🎨 Color Guide")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div style="background: #10b981; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">Positions 1-10<br>Excellent</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div style="background: #facc15; padding: 10px; border-radius: 5px; text-align: center; color: #1a1a1a; font-weight: bold;">Positions 11-20<br>Good</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div style="background: #f97316; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">Positions 21-50<br>Needs Work</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div style="background: #dc2626; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">Positions 51+<br>Poor</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div style="background: #374151; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">Not Ranking<br>Content Gap</div>', unsafe_allow_html=True)

else:
    # Instructions when no files uploaded
    st.info("👆 Please upload both CSV files to get started!")
    
    # Attribution Section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e3a8a, #1e40af); border-radius: 10px; margin: 20px 0;">
        <p style="color: #e0e7ff; font-size: 16px; margin: 0;">
            <strong style="color: white; font-size: 18px;">Created by Jon Clark</strong><br>
            Managing Partner at 
            <a href="https://www.movingtrafficmedia.com" target="_blank" style="color: #93c5fd; text-decoration: none; font-weight: 600;">Moving Traffic Media</a>, 
            an AI-driven search agency.
            <br><br>
            <a href="https://www.linkedin.com/in/ppcmarketing" target="_blank" 
               style="display: inline-block; background: #0077b5; color: white; padding: 10px 20px; 
               border-radius: 6px; text-decoration: none; font-weight: 600; margin-top: 10px;">
               🔗 Follow on LinkedIn
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📖 How to Use This Tool")
    
    # Create instruction cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 1️⃣ Export from Qforia
        Go to [**Qforia: Query Fan-Out Simulator**](https://ipullrank.com/tools/qforia) 
        and export your query fan-out results.
        """)
        
        st.markdown("""
        #### 3️⃣ Upload Your Files
        Use the upload boxes at the top to upload both CSV files.
        """)
        
        st.markdown("""
        #### 5️⃣ Get AI Analysis
        Click any AI assistant button (ChatGPT, Claude, Gemini, Perplexity, or Grok) 
        to get strategic recommendations and an action plan.
        """)
    
    with col2:
        st.markdown("""
        #### 2️⃣ Export from Google Search Console
        In Google Search Console, search for your head term and 
        export the **"Queries"** file from the results.
        """)
        
        st.markdown("""
        #### 4️⃣ Review Results
        Check the stats dashboard, AI insights, and three heatmaps to 
        understand your query performance and content gaps.
        """)
        
        st.markdown("""
        #### 6️⃣ Export & Act
        Export your content gaps CSV and use the AI insights to 
        prioritize your content calendar.
        """)
    
    st.markdown("---")
    
    st.markdown("### 🎨 What You'll Get")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Three Heatmap Views**
        - Main position heatmap
        - Performance by query type
        - Performance by content format
        """)
    
    with col2:
        st.markdown("""
        **🤖 Five AI Assistants**
        - ChatGPT
        - Claude
        - Gemini
        - Perplexity
        - Grok
        """)
    
    with col3:
        st.markdown("""
        **📈 Key Insights**
        - Ranking queries
        - Content gaps
        - Top positions
        - Total clicks
        """)
    
    st.markdown("---")
    
    # Color Guide
    st.markdown("### 🎨 Color Guide")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div style="background: #10b981; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">
        Positions 1-10<br>Excellent
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #facc15; padding: 10px; border-radius: 5px; text-align: center; color: #1a1a1a; font-weight: bold;">
        Positions 11-20<br>Good
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #f97316; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">
        Positions 21-50<br>Needs Work
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: #dc2626; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">
        Positions 51+<br>Poor
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div style="background: #374151; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">
        Not Ranking<br>Content Gap
        </div>
        """, unsafe_allow_html=True)
