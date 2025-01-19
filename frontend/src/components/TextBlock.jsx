/* TextBlock.jsx */
import React, { useState } from "react";
import api from "../services/api";
import "../styles/TextBlock.css";


function TextBlock({ block, onBlockChange }) {
  const [content, setContent] = useState(block.textblock?.content || "");
  const [isEditing, setIsEditing] = useState(false);

  const saveChanges = async () => {
    try {
      await api.put(`/dashboard/blocks/${block.id}/`, {
        block_type: "text",
        textblock: { content },
        position: block.position,
      });
      setIsEditing(false);
      onBlockChange();
    } catch (err) {
      console.error(err);
    }
  };

  if (isEditing) {
    return (
      <div className="text-block">
        <textarea
          className="text-block__textarea"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={4}
        />
        <div className="text-block__controls">
          <button onClick={saveChanges}>Save</button>
          <button onClick={() => setIsEditing(false)}>Cancel</button>
        </div>
      </div>
    );
  }

  return (
    <div className="text-block">
      <p className="text-block__content">{content}</p>
      <div className="text-block__controls">
        <button onClick={() => setIsEditing(true)}>Edit</button>
      </div>
    </div>
  );
}

export default TextBlock;
