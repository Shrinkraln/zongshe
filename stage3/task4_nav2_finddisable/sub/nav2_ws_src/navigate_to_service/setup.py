from setuptools import setup

package_name = "navigate_to_service"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="G42",
    maintainer_email="g42@course.local",
    description="第4课 navigate_to 服务节点：封装 Nav2 NavigateToPose（PPT P8/P15 契约）",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "navigate_to_service = navigate_to_service.navigate_to_service:main",
        ],
    },
)
