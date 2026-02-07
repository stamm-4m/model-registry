window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

window.dashAgGridComponentFunctions.StatusRenderer = function (props) {
    return props.value === "online" ? "🟢" : "🔴";
};

window.dashAgGridComponentFunctions.EditIconRenderer = function () {
    return "✏️";
};
window.dashAgGridComponentFunctions.RegisterToRenderer = function () {
    return React.createElement(
        "img",
        {
            src: "/assets/icon-ibisba.svg",
            style: {
                height: "46px",
                marginRight: "10px",
                verticalAlign: "middle",
                cursor: "pointer"
            },
            title: "Register to IBISBA",
            alt: "Register to IBISBA"      

        }
    );
};
  
window.dashAgGridComponentFunctions.DeleteIconRenderer = function () {
    return "🗑️";
}