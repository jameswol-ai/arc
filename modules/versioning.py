# Inside the save button
if col_save.button("Save to Library"):
    # Get current versions
    versions = mem["designs"] if "designs" in mem else []
    new_version = {
        "id": asset["id"],
        "type": asset["type"],
        "country": asset["country"],
        "soil": asset["soil_name"],
        "total_gfa": asset["total_gfa"],
        "scores": asset["scores"],
        "plan": asset["plan"],
        "timestamp": datetime.now().isoformat()
    }
    versions.append(new_version)
    mem["designs"] = versions
    save_memory(username, mem)
    st.success("Design saved!")


with st.expander("Version History", expanded=False):
    if mem["designs"]:
        for idx, ver in enumerate(mem["designs"]):
            st.write(f"{idx+1}. {ver['type']} - {ver['timestamp']}")
    else:
        st.write("No saved versions.")