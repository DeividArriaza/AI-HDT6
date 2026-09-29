module.exports = (output, context) => {
  const metadata = context?.providerResponse?.metadata || context?.metadata || {};
  const request = JSON.parse(context?.vars?.request || "{}");
  const weatherRequest = Boolean(request.requested_date) || /clima|tiempo|viento|lluvia|saltar/i.test(request.question || "");
  if (metadata.offline !== true || metadata.tool_selected !== (weatherRequest ? "weather" : "faq")) {
    return false;
  }

  // Dates outside the supported forecast window must be rejected before the
  // weather integration is called; all valid requests must execute it.
  if (weatherRequest && request.requested_date) {
    const days = (new Date(`${request.requested_date}T00:00:00Z`) - new Date(`${metadata.evaluation_today}T00:00:00Z`)) / 86400000;
    return metadata.tool_executed === (days >= 0 && days <= 16);
  }
  return metadata.tool_executed === true;
};
