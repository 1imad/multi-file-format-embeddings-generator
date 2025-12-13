import { MdClose, MdCode } from 'react-icons/md';
import './HtmlPreviewModal.css';

interface HtmlPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  htmlContent: string;
}

export default function HtmlPreviewModal({ isOpen, onClose, htmlContent }: HtmlPreviewModalProps) {
  if (!isOpen) return null;

  return (
    <div className="html-preview-overlay" onClick={onClose}>
      <div className="html-preview-modal" onClick={(e) => e.stopPropagation()}>
        <div className="html-preview-header">
          <div className="html-preview-title">
            <MdCode />
            <h3>HTML Preview</h3>
          </div>
          <button className="btn-close-preview" onClick={onClose}>
            <MdClose />
          </button>
        </div>
        <div className="html-preview-body">
          <iframe
            srcDoc={htmlContent}
            sandbox="allow-scripts"
            title="HTML Preview"
            className="html-preview-iframe"
          />
        </div>
      </div>
    </div>
  );
}
