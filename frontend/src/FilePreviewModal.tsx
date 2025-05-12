import React, { useState } from "react";
import { Document } from "react-pdf";
import Modal from "react-bootstrap/Modal";

type FilePreviewModalProps = {
  file: File;
};

function FilePreviewModal({ file }: FilePreviewModalProps) {
  return (
    <Modal show={true} size="lg" centered>
      <Modal.Header closeButton></Modal.Header>
      <Modal.Body>
        <Document file={file} />
      </Modal.Body>
    </Modal>
  );
}

export default FilePreviewModal;
