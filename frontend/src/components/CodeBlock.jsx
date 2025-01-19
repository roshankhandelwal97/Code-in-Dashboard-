/* CodeBlock.jsx */
import React, { useState } from "react";
import { Controlled as CodeMirror } from "react-codemirror2";
import api from "../services/api";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/python/python";
import "../styles/CodeBlock.css";


function CodeBlock({ block, onBlockChange }) {
  const [code, setCode] = useState(block.codeblock?.code || "");
  const [output, setOutput] = useState(block.codeblock?.output || "");
  const [aiPrompt, setAiPrompt] = useState("");

  const handleRunCode = async () => {
    try {
      // Update block code
      await api.put(`/dashboard/blocks/${block.id}/`, {
        block_type: "code",
        codeblock: { language: "python", code },
        position: block.position,
      });
      // Then run
      const response = await api.post(`/dashboard/blocks/${block.id}/run/`);
      setOutput(response.data.codeblock.output);
      onBlockChange();
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerateCode = async () => {
    if (!aiPrompt) {
      alert("Please enter a prompt for the AI");
      return;
    }
    try {
      const response = await api.post(
        `/dashboard/blocks/${block.id}/generate_code/`,
        { prompt: aiPrompt }
      );
      const newCode = response.data.codeblock.code;
      setCode(newCode);
      setAiPrompt("");
      alert("Code generated successfully!");
      onBlockChange();
    } catch (err) {
      console.error(err);
      alert("Error generating code");
    }
  };

  return (
    <div className="code-block">
      <CodeMirror
        className="code-block__editor"
        value={code}
        options={{
          mode: "python",
          theme: "default",
          lineNumbers: true,
        }}
        onBeforeChange={(editor, data, value) => {
          setCode(value);
        }}
      />
      <div className="code-block__buttons">
        <button onClick={handleRunCode}>Run</button>
      </div>

      <pre className="code-block__output">{output}</pre>

      <div className="code-block__ai">
        <input
          className="code-block__ai-prompt"
          placeholder="Ask AI to modify code..."
          value={aiPrompt}
          onChange={(e) => setAiPrompt(e.target.value)}
        />
        <button onClick={handleGenerateCode}>Generate Code</button>
      </div>
    </div>
  );
}

export default CodeBlock;
