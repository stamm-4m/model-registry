window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

window.dashAgGridComponentFunctions.StatusRenderer = function (props) {
    return props.value === "online" ? "🟢" : "🔴";
};

window.dashAgGridComponentFunctions.EditIconRenderer = function () {
    return "✏️";
};
