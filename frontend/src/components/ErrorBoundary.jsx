import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#09090b] text-zinc-100 flex items-center justify-center p-6">
          <div className="max-w-md w-full p-6 rounded-2xl bg-zinc-900 border border-zinc-800 shadow-2xl text-center space-y-4">
            <div className="inline-flex p-3 rounded-2xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <AlertTriangle className="h-8 w-8" />
            </div>
            <h2 className="text-lg font-bold text-white">Application Exception Caught</h2>
            <p className="text-xs text-zinc-400 leading-relaxed">
              {this.state.error?.message || 'An unexpected rendering error occurred. The system protected your state.'}
            </p>
            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-black font-semibold text-xs transition shadow-lg shadow-sky-500/20"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Reload Application</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
