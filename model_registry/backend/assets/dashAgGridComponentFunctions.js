window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

window.dashAgGridComponentFunctions.StatusRenderer = function (props) {
    return  props.value === "online" ? React.createElement("i", {className: "bi bi-check-circle-fill icon-column", title: "Online", alt: "Online"}) : React.createElement("i", {className: "bi bi-x-circle icon-column", title: "Offline", alt: "Offline"});
};

window.dashAgGridComponentFunctions.EditIconRenderer = function () {
    return React.createElement(
        "i",
        {
            className: "bi bi-pencil-square icon-column",
            title: "Edit",
            alt: "Edit"      

        }
    );
};
window.dashAgGridComponentFunctions.RegisterToRenderer = function () {
    return React.createElement(
        "img",
        {
            src: "/assets/icon-ibisba.svg",
            className: "icon-column",
            title: "Register to IBISBA",
            alt: "Register to IBISBA"      

        }
    );
};

window.dashAgGridComponentFunctions.XAIRenderer = function () {
    return React.createElement(
        "i",
        {
            className: "bi bi-search icon-column",
            title: "Explainability",
            alt: "Explainability"      

        }
    );
};
  
window.dashAgGridComponentFunctions.DeleteIconRenderer = function () {
    return React.createElement(
        "i",
        {
            className: "bi bi-trash icon-column",
            title: "Delete",
            alt: "Delete"      

        }
    );
}

window.dashAgGridComponentFunctions.DetailsIconRenderer = function () {
    return React.createElement(
        "i",
        {
            className: "bi bi-eye-fill icon-column",
            title: "Details",
            alt: "Details"      

        }
    );
}