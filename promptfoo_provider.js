const { spawnSync } = require("node:child_process");
const path = require("node:path");

class Hdt5LocalProvider {
  id() {
    return "hdt5-local-fixtures";
  }

  async callApi(prompt) {
    const request = typeof prompt === "string" ? JSON.parse(prompt) : prompt;
    const completed = spawnSync(
      process.env.PYTHON || "python3",
      [path.join(__dirname, "hdt5_adapter.py"), JSON.stringify(request)],
      { encoding: "utf8" },
    );
    if (completed.status !== 0) {
      throw new Error(completed.stderr || "HDT-5 adapter failed");
    }
    const result = JSON.parse(completed.stdout);
    const citations = result.metadata.citations || [];
    const output = citations.length
      ? `${result.answer}\nCitas: ${citations.join(", ")}`
      : result.answer;
    return { output, metadata: result.metadata };
  }
}

module.exports = Hdt5LocalProvider;
