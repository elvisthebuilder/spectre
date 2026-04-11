import React, { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { io } from 'socket.io-client';
import { 
  Activity, 
  Target, 
  Share2, 
  Zap, 
  AlertCircle, 
  ChevronRight, 
  Search,
  Download,
  Maximize2,
  X
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const SOCKET_URL = 'http://localhost:8000';

function App() {
  const [socket, setSocket] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [missionLogs, setMissionLogs] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [missionActive, setMissionActive] = useState(false);
  const [missionParams, setMissionParams] = useState({ name: '', handle: '', email: '' });
  const [graphDims, setGraphDims] = useState({ width: 800, height: 600 });
  const [expandedPanel, setExpandedPanel] = useState(null);
  
  const fgRef = useRef();
  const graphContainerRef = useRef(null);

  // Initialize Socket.IO
  useEffect(() => {
    // Setup resize observer for dynamic graph sizing
    const observer = new ResizeObserver(entries => {
      if (entries[0] && entries[0].contentRect) {
        setGraphDims({
          width: entries[0].contentRect.width,
          height: entries[0].contentRect.height
        });
      }
    });
    if (graphContainerRef.current) {
      observer.observe(graphContainerRef.current);
    }

    const newSocket = io(SOCKET_URL);
    setSocket(newSocket);

    newSocket.on('connect', () => {
      addLog("Neural Handshake Established. Secure link active.", "system");
    });

    newSocket.on('discovery_event', (event) => {
      if (event.type === 'NODE_FOUND') {
        const newNode = event.data;
        setGraphData(prev => ({
          ...prev,
          nodes: prev.nodes.some(n => n.id === newNode.id)
            ? prev.nodes
            : [...prev.nodes, newNode]
        }));
        addLog(`Located: ${newNode.label}${newNode.url ? ` → ${newNode.url}` : ''}`, "discovery");
      } else if (event.type === 'LINK_FOUND') {
        const newLink = event.data;
        setGraphData(prev => ({
          ...prev,
          links: prev.links.some(l => l.source === newLink.source && l.target === newLink.target)
            ? prev.links
            : [...prev.links, newLink]
        }));
      } else if (event.type === 'LINK_REMOVE') {
        const linkToRemove = event.data;
        setGraphData(prev => ({
          ...prev,
          links: prev.links.filter(l => !(
            (l.source.id === linkToRemove.source || l.source === linkToRemove.source) && 
            (l.target.id === linkToRemove.target || l.target === linkToRemove.target)
          ))
        }));
      } else if (event.type === 'STATUS_UPDATE') {
        addLog(event.data, "system");
      } else if (event.type === 'INTEL_REPORT') {
        addLog(`Intel Report Received`, "system");
        setGraphData(prev => ({
          ...prev,
          nodes: prev.nodes.map(n => 
            n.id === event.data.node_id 
              ? { ...n, description: event.data.content } 
              : n
          )
        }));
        setSelectedNode(prev => 
          prev?.id === event.data.node_id 
            ? { ...prev, description: event.data.content } 
            : prev
        );
      }
    });

    return () => newSocket.close();
  }, []);

  const addLog = (message, type = "info") => {
    setMissionLogs(prev => [{
      id: Date.now(),
      time: new Date().toLocaleTimeString(),
      message,
      type
    }, ...prev].slice(0, 50));
  };

  const startMission = () => {
    if (!missionParams.name && !missionParams.handle) return;
    setMissionActive(true);
    setGraphData({ nodes: [], links: [] });
    addLog(`Initiating reconnaissance for ${missionParams.name || missionParams.handle}...`, "system");
    socket.emit('initiate_mission', missionParams);
  };

  const onNodeClick = useCallback(node => {
    setSelectedNode(node);
    // Aim at node
    fgRef.current.centerAt(node.x, node.y, 1000);
    fgRef.current.zoom(3, 1000);
  }, []);

  return (
    <div className="spectre-container">
      <header className="spectre-header">
        <div className="logo">
          <Zap size={24} fill="#00f2ff" />
          Project Spectre
        </div>
        <div className="status-indicator">
          <div className="dot"></div>
          SECURE CHANNEL: {socket?.connected ? 'ACTIVE' : 'OFFLINE'}
        </div>
      </header>

      <main className="dashboard-main">
        {/* Left: Intelligence Graph */}
        <section className="graph-pane" ref={graphContainerRef} style={{ overflow: 'hidden' }}>
          <ForceGraph2D
            ref={fgRef}
            width={graphDims.width}
            height={graphDims.height}
            graphData={graphData}
            backgroundColor="transparent"
            nodeRelSize={6}
            nodeColor={node => {
              if (node.type === 'USER') return '#00f2ff';
              if (node.confidence === 1.0) return '#00f2ff';   // Verified/Claimed
              if (node.confidence >= 0.6) return '#f0a500';    // Unknown (bot-blocked)
              return '#6e7681';                                 // Possible (low confidence)
            }}
            nodeLabel={node => `${node.label}: ${node.description || ''}`}
            linkColor={() => 'rgba(132, 141, 151, 0.2)'}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.005}
            onNodeClick={onNodeClick}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = node.label;
              const fontSize = 12/globalScale;
              ctx.font = `${fontSize}px Inter`;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillStyle = node.type === 'USER' ? '#00f2ff' : '#e6edf3';
              ctx.fillText(label, node.x, node.y + (node.type === 'USER' ? 12 : 10));
              
              // Draw node circle
              ctx.beginPath();
              ctx.arc(node.x, node.y, node.type === 'USER' ? 6 : 4, 0, 2 * Math.PI, false);
              ctx.fillStyle = node.type === 'USER' ? '#00f2ff' : '#30363d';
              ctx.fill();
              if (node.type === 'USER') {
                ctx.strokeStyle = 'rgba(0, 242, 255, 0.5)';
                ctx.lineWidth = 2;
                ctx.stroke();
              }
            }}
          />
          
          {!missionActive && (
            <div className="mission-briefing glass" style={{
              position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
              width: '400px', padding: '32px', zIndex: 100
            }}>
              <h2 style={{ color: '#00f2ff', marginBottom: '16px', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Target size={18} /> Mission Parameters
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <input 
                  type="text" 
                  placeholder="Target Full Name" 
                  className="mission-input"
                  value={missionParams.name}
                  onChange={e => setMissionParams({...missionParams, name: e.target.value})}
                  style={{ background: '#0d1117', border: '1px solid #30363d', padding: '12px', color: '#fff', borderRadius: '4px' }}
                />
                <input 
                  type="text" 
                  placeholder="Primary Handle / Alias" 
                  className="mission-input"
                  value={missionParams.handle}
                  onChange={e => setMissionParams({...missionParams, handle: e.target.value})}
                  style={{ background: '#0d1117', border: '1px solid #30363d', padding: '12px', color: '#fff', borderRadius: '4px' }}
                />
                <button 
                  onClick={startMission}
                  style={{ background: '#00f2ff', color: '#05070a', border: 'none', padding: '12px', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                >
                  <Search size={18} /> Initiate OSINT Sweep
                </button>
              </div>
            </div>
          )}
        </section>

        {/* Right: Inspector & Feed */}
        <aside className="sidebar-right">
          {/* Node Inspector */}
          <div className="inspector glass">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '0.8rem', color: '#848d97', textTransform: 'uppercase', margin: 0 }}>Entity Inspector</h3>
              <Maximize2 size={14} style={{ cursor: 'pointer', color: '#848d97' }} onClick={() => setExpandedPanel('inspector')} />
            </div>
            {selectedNode ? (
              <div>
                <div style={{ fontSize: '1.2rem', color: '#00f2ff', fontWeight: 'bold' }}>{selectedNode.label}</div>
                <div style={{ fontSize: '0.8rem', color: '#848d97', marginTop: '4px' }}>{selectedNode.type}</div>
                <div className="markdown-container" style={{ fontSize: '0.9rem', marginTop: '16px', lineHeight: '1.5', color: '#e6edf3' }}>
                  <ReactMarkdown>{selectedNode.description || ''}</ReactMarkdown>
                </div>
                {selectedNode.url && (
                  <a href={selectedNode.url} target="_blank" rel="noopener noreferrer" style={{ color: '#00f2ff', fontSize: '0.8rem', display: 'block', marginTop: '12px' }}>
                    View External Dossier <ChevronRight size={14} style={{ verticalAlign: 'middle' }} />
                  </a>
                )}
                <button 
                  style={{ marginTop: '24px', width: '100%', background: 'rgba(0, 242, 255, 0.1)', border: '1px solid #00f2ff', color: '#00f2ff', padding: '10px', borderRadius: '4px', fontSize: '0.8rem', cursor: 'pointer' }}
                >
                  Initiate Deep-Dive Sequence
                </button>
              </div>
            ) : (
             <div style={{ color: '#848d97', fontSize: '0.85rem', textAlign: 'center', marginTop: '40px' }}>Select a node in the graph to inspect discovery details.</div>
            )}
          </div>

          <div className="mission-feed glass">
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
               <h3 style={{ fontSize: '0.8rem', color: '#848d97', textTransform: 'uppercase', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={14} /> Mission Feed
              </h3>
              <Maximize2 size={14} style={{ cursor: 'pointer', color: '#848d97' }} onClick={() => setExpandedPanel('feed')} />
            </div>
            {missionLogs.map(log => (
              <div key={log.id} className="feed-item">
                <div className="time">[{log.time}]</div>
                <div className="message" style={{ color: log.type === 'discovery' ? '#00f2ff' : '#e6edf3' }}>{log.message}</div>
              </div>
            ))}
          </div>
        </aside>
      </main>

      {/* Expansion Modal Overlay */}
      {expandedPanel && (
        <div 
          style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(5, 7, 10, 0.8)', zIndex: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px' }}
          onClick={() => setExpandedPanel(null)}
        >
          <div 
            className="glass" 
            style={{ width: '80%', maxWidth: '1000px', height: '80%', display: 'flex', flexDirection: 'column', position: 'relative' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
               <h2 style={{ color: '#00f2ff', fontSize: '1.2rem', margin: 0 }}>
                 {expandedPanel === 'inspector' ? 'Entity Inspector (Expanded)' : 'Mission Feed (Expanded)'}
               </h2>
               <X size={20} style={{ cursor: 'pointer', color: '#848d97' }} onClick={() => setExpandedPanel(null)} />
            </div>
            
            <div style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
              {expandedPanel === 'inspector' && selectedNode ? (
                <div>
                  <div style={{ fontSize: '1.5rem', color: '#00f2ff', fontWeight: 'bold' }}>{selectedNode.label}</div>
                  <div style={{ fontSize: '1rem', color: '#848d97', marginTop: '4px' }}>{selectedNode.type}</div>
                  
                  <div className="markdown-container" style={{ fontSize: '1rem', marginTop: '24px', lineHeight: '1.6', color: '#e6edf3' }}>
                    <ReactMarkdown>{selectedNode.description || ''}</ReactMarkdown>
                  </div>
                  
                  {selectedNode.url && (
                    <a href={selectedNode.url} target="_blank" rel="noopener noreferrer" style={{ color: '#00f2ff', fontSize: '1rem', display: 'block', marginTop: '24px' }}>
                      View External Dossier <ChevronRight size={16} style={{ verticalAlign: 'middle' }} />
                    </a>
                  )}
                </div>
              ) : null}

              {expandedPanel === 'inspector' && !selectedNode && (
                <div style={{ color: '#848d97', textAlign: 'center', marginTop: '100px' }}>No entity selected.</div>
              )}

              {expandedPanel === 'feed' && (
                <div>
                  {missionLogs.map(log => (
                    <div key={log.id} className="feed-item" style={{ marginBottom: '16px', paddingBottom: '16px' }}>
                      <div className="time" style={{ fontSize: '0.85rem' }}>[{log.time}]</div>
                      <div className="message" style={{ fontSize: '1rem', color: log.type === 'discovery' ? '#00f2ff' : '#e6edf3', marginTop: '8px' }}>{log.message}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
