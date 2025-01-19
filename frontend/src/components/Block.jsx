/* Block.jsx */
import React from "react";
import TextBlock from "./TextBlock";
import CodeBlock from "./CodeBlock";
import "../styles/Block.css";


function Block({ block, onBlockChange }) {
  return (
    <div className="block">
      {block.block_type === "text" ? (
        <TextBlock block={block} onBlockChange={onBlockChange} />
      ) : block.block_type === "code" ? (
        <CodeBlock block={block} onBlockChange={onBlockChange} />
      ) : (
        <div>Unknown block type</div>
      )}
    </div>
  );
}

export default Block;
