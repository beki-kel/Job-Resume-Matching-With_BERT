/**
 * File Upload Component with drag & drop
 */
'use client';

import { useCallback, useState } from 'react';
import { DocumentUpload, DocumentText, CloseCircle } from 'iconsax-react';
import { motion, AnimatePresence } from 'framer-motion';
import { validateFile } from '@/lib/utils';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing?: boolean;
}

export const FileUpload = ({ onFileSelect, isProcessing }: FileUploadProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    setError(null);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const validation = validateFile(files[0]);
      if (validation.valid) {
        setSelectedFile(files[0]);
        onFileSelect(files[0]);
      } else {
        setError(validation.error || 'Invalid file');
      }
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const files = e.target.files;
    if (files && files[0]) {
      const validation = validateFile(files[0]);
      if (validation.valid) {
        setSelectedFile(files[0]);
        onFileSelect(files[0]);
      } else {
        setError(validation.error || 'Invalid file');
      }
    }
  }, [onFileSelect]);

  const clearFile = () => {
    setSelectedFile(null);
    setError(null);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <AnimatePresence mode="wait">
        {!selectedFile ? (
          <motion.div
            key="upload"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`glass-card p-12 text-center cursor-pointer transition-all duration-300 ${
              isDragging ? 'border-blue-500 bg-blue-500/10 scale-105' : ''
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              onChange={handleFileInput}
              className="hidden"
              disabled={isProcessing}
            />

            <motion.div
              animate={{ y: isDragging ? -10 : 0 }}
              className="flex flex-col items-center gap-4"
            >
              <div className="p-6 rounded-full glass-card glow">
                <DocumentUpload size={48} variant="Bold" color="#ffffff" />
              </div>

              <div>
                <h3 className="text-2xl font-semibold mb-2">
                  Upload Your Resume
                </h3>
                <p className="text-white/60">
                  Drag and drop your PDF file here, or click to browse
                </p>
                <p className="text-sm text-white/40 mt-2">
                  Maximum file size: 5MB
                </p>
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="px-4 py-2 rounded-lg glass-card border-red-500/50 text-red-400 text-sm"
                >
                  {error}
                </motion.div>
              )}
            </motion.div>
          </motion.div>
        ) : (
          <motion.div
            key="selected"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="glass-card p-6"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl glass-card glow">
                  <DocumentText size={24} variant="Bold" color="#ffffff" />
                </div>
                <div>
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-white/60">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>

              {!isProcessing && (
                <button
                  onClick={clearFile}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <CloseCircle size={20} variant="Bold" color="#ffffff" />
                </button>
              )}
            </div>

            {isProcessing && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-4 pt-4 border-t border-white/10"
              >
                <div className="flex items-center gap-3">
                  <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-linear-to-r from-white/50 to-white/80"
                      initial={{ width: '0%' }}
                      animate={{ width: '100%' }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </div>
                </div>
                <p className="text-sm text-white/60 mt-2">
                  Processing your resume with AI...
                </p>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
